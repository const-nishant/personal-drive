// Index File Function
// Downloads file from S3, extracts text, indexes it via semantic service
// Updates metadata with hash, storagePath, and indexing status

import { Client, Databases, Query } from "node-appwrite";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import crypto from "crypto";
import { Readable } from "stream";

/**
 * @param {object} context - The Appwrite function context
 * @param {object} req - The request object
 */
export default async function (context, req) {
  try {
    // Initialize Appwrite client
    const client = new Client()
      .setEndpoint(context.APPWRITE_FUNCTION_ENDPOINT)
      .setProject(context.APPWRITE_FUNCTION_PROJECT_ID)
      .setKey(context.APPWRITE_FUNCTION_API_KEY);

    const databases = new Databases(client);

    // Get user ID from request
    const userId = req.headers["x-appwrite-user-id"] || req.body?.userId;
    if (!userId) {
      return context.res.json(
        {
          success: false,
          error: "User authentication required",
        },
        401
      );
    }

    // Parse request body
    const body = typeof req.body === "string" ? JSON.parse(req.body) : req.body;
    const { fileId } = body;

    if (!fileId) {
      return context.res.json(
        {
          success: false,
          error: "fileId is required",
        },
        400
      );
    }

    // Validate fileId format (alphanumeric + hyphens only)
    if (!/^[a-zA-Z0-9_-]+$/.test(fileId)) {
      return context.res.json(
        {
          success: false,
          error: "Invalid fileId format",
        },
        400
      );
    }

    const collectionId = context.env.FILES_COLLECTION_ID || "files";
    const databaseId = context.env.APPWRITE_DATABASE_ID || "default";

    // Fetch file metadata from database
    let document;
    try {
      // Query by fileId (not document ID)
      const documents = await databases.listDocuments(
        databaseId,
        collectionId,
        [Query.equal("fileId", fileId)]
      );

      if (documents.documents.length === 0) {
        return context.res.json(
          {
            success: false,
            error: "File not found",
          },
          404
        );
      }

      document = documents.documents[0];

      // Verify user owns the file
      if (document.userId !== userId) {
        return context.res.json(
          {
            success: false,
            error: "Unauthorized to index this file",
          },
          403
        );
      }

      // Check if already indexed
      if (document.indexed === true) {
        return context.res.json({
          success: true,
          message: "File already indexed",
          fileId,
          indexed: true,
        });
      }
    } catch (error) {
      console.error("Error fetching file metadata:", error);
      return context.res.json(
        {
          success: false,
          error: "Failed to fetch file metadata",
        },
        500
      );
    }

    const { storagePath, mimeType, name } = document;

    if (!storagePath) {
      return context.res.json(
        {
          success: false,
          error: "Storage path not found in metadata",
        },
        400
      );
    }

    // Initialize S3 client
    const s3Client = new S3Client({
      endpoint: context.env.S3_ENDPOINT,
      region: context.env.S3_REGION || "us-east-1",
      credentials: {
        accessKeyId: context.env.S3_ACCESS_KEY_ID,
        secretAccessKey: context.env.S3_SECRET_ACCESS_KEY,
      },
      forcePathStyle: true,
    });

    // Download file from S3
    let fileBuffer;
    try {
      const getObjectCommand = new GetObjectCommand({
        Bucket: context.env.S3_BUCKET_NAME,
        Key: storagePath,
      });

      const response = await s3Client.send(getObjectCommand);

      // Convert stream to buffer
      const chunks = [];
      for await (const chunk of response.Body) {
        chunks.push(chunk);
      }
      fileBuffer = Buffer.concat(chunks);
    } catch (error) {
      console.error("Error downloading file from S3:", error);

      // Update status to failed
      await databases.updateDocument(databaseId, collectionId, document.$id, {
        status: "failed",
      });

      return context.res.json(
        {
          success: false,
          error: "Failed to download file from storage",
        },
        500
      );
    }

    // Compute SHA-256 hash
    const hash = crypto.createHash("sha256").update(fileBuffer).digest("hex");

    // Check for deduplication (if hash exists, reuse existing file)
    const existingFiles = await databases.listDocuments(
      databaseId,
      collectionId,
      [Query.equal("hash", hash), Query.equal("userId", userId)]
    );

    if (
      existingFiles.documents.length > 0 &&
      existingFiles.documents[0].fileId !== fileId
    ) {
      // File with same hash exists, reuse storage path
      const existingFile = existingFiles.documents[0];

      // Update current file to use existing storage path
      await databases.updateDocument(databaseId, collectionId, document.$id, {
        hash,
        storagePath: existingFile.storagePath,
        status: "indexed",
        indexed: true,
      });

      return context.res.json({
        success: true,
        message: "File indexed (duplicate detected, reused existing file)",
        fileId,
        hash,
        duplicate: true,
        originalFileId: existingFile.fileId,
      });
    }

    // Extract text based on MIME type
    let extractedText = "";

    try {
      if (mimeType === "application/pdf") {
        // PDF text extraction
        const pdfParse = await import("pdf-parse");
        const pdfData = await pdfParse.default(fileBuffer);
        extractedText = pdfData.text;
      } else if (
        mimeType ===
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
        mimeType === "application/msword"
      ) {
        // DOCX text extraction
        const mammoth = await import("mammoth");
        const result = await mammoth.extractRawText({ buffer: fileBuffer });
        extractedText = result.value;
      } else if (mimeType === "text/plain") {
        // Plain text
        extractedText = fileBuffer.toString("utf-8");
      } else if (mimeType.startsWith("image/")) {
        // Images: Use filename and metadata as text
        // For full OCR, you would need tesseract.js or similar (heavy dependency)
        extractedText = `Image file: ${name}. ${document.description || ""}`;
      } else {
        // Unsupported type, use filename and description
        extractedText = `File: ${name}. ${document.description || ""}`;
      }

      // Clean and limit text (semantic service may have limits)
      extractedText = extractedText.trim().substring(0, 100000); // Limit to 100KB of text

      if (!extractedText || extractedText.length === 0) {
        extractedText = `File: ${name}`; // Fallback to filename
      }
    } catch (error) {
      console.error("Error extracting text:", error);
      // Use filename as fallback
      extractedText = `File: ${name}. ${document.description || ""}`;
    }

    // Call semantic service to index
    const semanticServiceUrl = context.env.SEMANTIC_SERVICE_URL;
    const semanticServiceApiKey = context.env.SEMANTIC_SERVICE_API_KEY;

    if (!semanticServiceUrl) {
      return context.res.json(
        {
          success: false,
          error: "Semantic service URL not configured",
        },
        500
      );
    }

    try {
      const indexResponse = await fetch(`${semanticServiceUrl}/index`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": semanticServiceApiKey || "",
        },
        body: JSON.stringify({
          file_id: fileId,
          text: extractedText,
        }),
      });

      if (!indexResponse.ok) {
        const errorData = await indexResponse
          .json()
          .catch(() => ({ detail: "Unknown error" }));
        throw new Error(
          errorData.detail || `Semantic service error: ${indexResponse.status}`
        );
      }

      const indexResult = await indexResponse.json();

      // Update metadata with hash, indexing status
      await databases.updateDocument(databaseId, collectionId, document.$id, {
        hash,
        indexed: true,
        status: "indexed",
        vectorId: indexResult.vectorId || null,
      });

      return context.res.json({
        success: true,
        message: "File indexed successfully",
        fileId,
        hash,
        indexed: true,
        textLength: extractedText.length,
      });
    } catch (error) {
      console.error("Error calling semantic service:", error);

      // Update status to failed
      await databases.updateDocument(databaseId, collectionId, document.$id, {
        hash,
        status: "failed",
      });

      return context.res.json(
        {
          success: false,
          error: `Indexing failed: ${error.message}`,
        },
        500
      );
    }
  } catch (error) {
    console.error("Error in indexFile function:", error);
    return context.res.json(
      {
        success: false,
        error: error.message || "Internal server error",
      },
      500
    );
  }
}
