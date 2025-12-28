// Presign Upload Function
// Generates pre-signed URLs for secure S3 uploads
// Creates initial metadata record in database

import { Client, ID, Databases } from "node-appwrite";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

/**
 * @param {object} context - The Appwrite function context
 * @param {object} req - The request object (contains body, headers, etc.)
 */
export default async function (context, req) {
  try {
    // Handle case where req might be undefined (HTTP execution)
    if (!req) {
      req = context.req || {};
    }

    // Initialize Appwrite client
    const client = new Client()
      .setEndpoint(context.APPWRITE_FUNCTION_ENDPOINT)
      .setProject(context.APPWRITE_FUNCTION_PROJECT_ID)
      .setKey(context.APPWRITE_FUNCTION_API_KEY);

    const databases = new Databases(client);

    // Parse request body
    // Appwrite provides bodyJson for HTTP executions via API
    // The data is passed in req.bodyJson.data or context.req.bodyJson.data
    let requestBody = req?.bodyJson || context.req?.bodyJson || {};

    // If bodyJson.data exists (HTTP execution format), extract it
    if (requestBody && typeof requestBody === "object" && requestBody.data !== undefined) {
      // Handle both string and object formats for data
      if (typeof requestBody.data === "string") {
        try {
          requestBody = JSON.parse(requestBody.data);
        } catch (e) {
          context.log("Failed to parse requestBody.data as JSON:", e.message);
          requestBody = {};
        }
      } else if (typeof requestBody.data === "object") {
        // data is already an object
        requestBody = requestBody.data;
      }
    } else if (!requestBody || (typeof requestBody === "object" && Object.keys(requestBody).length === 0)) {
      // Fallback: try to parse from body string or other locations
      const bodyString = req?.body || context.req?.body || "";
      if (bodyString && typeof bodyString === "string" && bodyString.trim()) {
        try {
          requestBody = JSON.parse(bodyString);
          // After parsing, check if it has a data property
          if (requestBody && typeof requestBody === "object" && requestBody.data) {
            requestBody = typeof requestBody.data === "string" 
              ? JSON.parse(requestBody.data) 
              : requestBody.data;
          }
        } catch (e) {
          context.log("Failed to parse body string as JSON:", e.message);
          requestBody = {};
        }
      } else {
        requestBody = {};
      }
    }

    // Debug logging (remove in production)
    context.log("Parsed requestBody:", JSON.stringify(requestBody));

    const {
      name,
      size,
      mimeType,
      folderId,
      description,
      tags,
      userId: bodyUserId,
    } = requestBody || {};

    // Use userId from body if not in headers
    // Check multiple header locations for user ID
    const headerUserId =
      req?.headers?.["x-appwrite-user-id"] ||
      context.req?.headers?.["x-appwrite-user-id"] ||
      req?.headers?.["X-Appwrite-User-Id"] ||
      context.req?.headers?.["X-Appwrite-User-Id"];

    const userId = headerUserId || bodyUserId;

    // Debug logging
    context.log(
      `userId from headers: ${headerUserId}, from body: ${bodyUserId}, final: ${userId}`
    );

    if (!userId) {
      return context.res.json(
        {
          success: false,
          error: "User authentication required",
        },
        401
      );
    }

    // Validate required fields
    if (!name || !size || !mimeType) {
      return context.res.json(
        {
          success: false,
          error: "Missing required fields: name, size, mimeType",
        },
        400
      );
    }

    // Validate file size (max 1GB)
    const MAX_FILE_SIZE = parseInt(context.env.MAX_FILE_SIZE || "1073741824"); // 1GB default
    if (size > MAX_FILE_SIZE) {
      return context.res.json(
        {
          success: false,
          error: `File size exceeds maximum allowed size of ${
            MAX_FILE_SIZE / 1024 / 1024
          }MB`,
        },
        400
      );
    }

    // Validate MIME type (whitelist)
    const ALLOWED_MIME_TYPES = (
      context.env.ALLOWED_MIME_TYPES ||
      "application/pdf,image/jpeg,image/png,image/jpg,image/gif,text/plain,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ).split(",");

    if (!ALLOWED_MIME_TYPES.includes(mimeType)) {
      return context.res.json(
        {
          success: false,
          error: `MIME type ${mimeType} is not allowed`,
        },
        400
      );
    }

    // Sanitize file name (prevent path traversal)
    const sanitizedName = name
      .replace(/[^a-zA-Z0-9._-]/g, "_")
      .substring(0, 255);
    if (!sanitizedName) {
      return context.res.json(
        {
          success: false,
          error: "Invalid file name",
        },
        400
      );
    }

    // Generate unique file ID
    const fileId = ID.unique();

    // Determine storage path based on MIME type
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");

    let storagePath;
    if (mimeType.startsWith("image/")) {
      // Photos: photos/YYYY/MM/filename.ext
      storagePath = `photos/${year}/${month}/${fileId}_${sanitizedName}`;
    } else {
      // Documents: documents/user_id/filename.ext
      storagePath = `documents/${userId}/${fileId}_${sanitizedName}`;
    }

    // Initialize S3 client
    const s3Client = new S3Client({
      endpoint: context.env.S3_ENDPOINT,
      region: context.env.S3_REGION || "us-east-1",
      credentials: {
        accessKeyId: context.env.S3_ACCESS_KEY_ID,
        secretAccessKey: context.env.S3_SECRET_ACCESS_KEY,
      },
      forcePathStyle: true, // Required for B2 and R2
    });

    // Create presigned URL for upload (15 minutes expiration)
    const command = new PutObjectCommand({
      Bucket: context.env.S3_BUCKET_NAME,
      Key: storagePath,
      ContentType: mimeType,
    });

    const presignedUrl = await getSignedUrl(s3Client, command, {
      expiresIn: 900, // 15 minutes
    });

    // Create initial metadata record in database
    const collectionId = context.env.FILES_COLLECTION_ID || "files";
    const document = await databases.createDocument(
      context.env.APPWRITE_DATABASE_ID || "default",
      collectionId,
      ID.unique(),
      {
        fileId,
        name: sanitizedName,
        size: parseInt(size),
        mimeType,
        userId,
        folderId: folderId || null,
        description: description || "",
        tags: tags || [],
        indexed: false,
        vectorId: null,
        hash: null,
        storagePath,
        createdAt: now.toISOString(),
        status: "pending",
      }
    );

    return context.res.json({
      success: true,
      fileId,
      presignedUrl,
      expiresIn: 900, // 15 minutes in seconds
      metadata: {
        fileId,
        name: sanitizedName,
        size: parseInt(size),
        mimeType,
        storagePath,
        createdAt: now.toISOString(),
      },
    });
  } catch (error) {
    console.error("Error in presignUpload function:", error);
    return context.res.json(
      {
        success: false,
        error: error.message || "Internal server error",
      },
      500
    );
  }
}
