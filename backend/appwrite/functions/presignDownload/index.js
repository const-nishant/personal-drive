// Presign Download Function
// Generates pre-signed URLs for secure S3 downloads on-demand
// Validates user ownership before generating URL

import { Client, Databases, Query } from "node-appwrite";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

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

    // Validate fileId format
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

    // Fetch file metadata and verify ownership
    let document;
    try {
      const documents = await databases.listDocuments(
        databaseId,
        collectionId,
        [Query.equal("fileId", fileId), Query.equal("userId", userId)],
        1
      );

      if (documents.documents.length === 0) {
        return context.res.json(
          {
            success: false,
            error: "File not found or unauthorized",
          },
          404
        );
      }

      document = documents.documents[0];
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

    // Create presigned URL for download (1 hour expiration)
    const command = new GetObjectCommand({
      Bucket: context.env.S3_BUCKET_NAME,
      Key: storagePath,
      ResponseContentDisposition: `attachment; filename="${name}"`,
      ResponseContentType: mimeType,
    });

    const presignedUrl = await getSignedUrl(s3Client, command, {
      expiresIn: 3600, // 1 hour
    });

    return context.res.json({
      success: true,
      fileId,
      presignedUrl,
      expiresIn: 3600, // 1 hour in seconds
      metadata: {
        fileId,
        name,
        mimeType,
        size: document.size,
      },
    });
  } catch (error) {
    console.error("Error in presignDownload function:", error);
    return context.res.json(
      {
        success: false,
        error: error.message || "Internal server error",
      },
      500
    );
  }
}
