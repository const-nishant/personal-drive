import { Client, Databases, Query } from "node-appwrite";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

/**
 * Appwrite Function: presignDownload
 * - Validates ownership
 * - Ensures file is indexed
 * - Generates time-bound S3 download URL
 */
export default async function presignDownload(context, req) {
  try {
    const request = req ?? context.req;
    if (!request) {
      return context.res.json(
        { success: false, error: "Invalid execution context" },
        400
      );
    }

    /* ----------------------------------------------------
     * Environment validation
     * -------------------------------------------------- */
    const {
      APPWRITE_FUNCTION_ENDPOINT,
      APPWRITE_FUNCTION_PROJECT_ID,
      APPWRITE_FUNCTION_API_KEY,
      APPWRITE_DATABASE_ID = "6950ec6400349318ed79",
      FILES_COLLECTION_ID = "6950ec640034b7a80a2d",

      S3_ENDPOINT,
      S3_ACCESS_KEY_ID,
      S3_SECRET_ACCESS_KEY,
      S3_BUCKET_NAME,
      S3_REGION,
    } = process.env;

    if (
      !APPWRITE_FUNCTION_ENDPOINT ||
      !APPWRITE_FUNCTION_PROJECT_ID ||
      !APPWRITE_FUNCTION_API_KEY ||
      !S3_ENDPOINT ||
      !S3_ACCESS_KEY_ID ||
      !S3_SECRET_ACCESS_KEY ||
      !S3_BUCKET_NAME
    ) {
      return context.res.json(
        { success: false, error: "Server configuration incomplete" },
        500
      );
    }

    /* ----------------------------------------------------
     * Request parsing
     * -------------------------------------------------- */
    context.log("RAW REQUEST:", {
      hasReq: !!request,
      hasBodyJson: !!request?.bodyJson,
      bodyJsonType: typeof request?.bodyJson,
      headers: request?.headers,
    });

    let body = {};
    if (request?.bodyJson && typeof request.bodyJson === "object") {
      body = request.bodyJson;
      if (typeof body.data === "string") {
        body = JSON.parse(body.data);
      } else if (typeof body.data === "object") {
        body = body.data;
      }
    }

    const { fileId, userId: bodyUserId } = body;
    const userId = request.headers?.["x-appwrite-user-id"] ?? bodyUserId;

    if (!userId) {
      return context.res.json(
        { success: false, error: "Authentication required" },
        401
      );
    }

    if (!fileId || !/^[a-zA-Z0-9_-]+$/.test(fileId)) {
      return context.res.json(
        { success: false, error: "Invalid or missing fileId" },
        400
      );
    }

    /* ----------------------------------------------------
     * Appwrite client
     * -------------------------------------------------- */
    const client = new Client()
      .setEndpoint(APPWRITE_FUNCTION_ENDPOINT)
      .setProject(APPWRITE_FUNCTION_PROJECT_ID)
      .setKey(APPWRITE_FUNCTION_API_KEY);

    const databases = new Databases(client);

    /* ----------------------------------------------------
     * Fetch file + verify ownership
     * -------------------------------------------------- */
    const docs = await databases.listDocuments(
      APPWRITE_DATABASE_ID,
      FILES_COLLECTION_ID,
      [Query.equal("fileId", fileId), Query.equal("userId", userId)]
    );

    if (docs.documents.length === 0) {
      return context.res.json(
        { success: false, error: "File not found or unauthorized" },
        404
      );
    }

    const file = docs.documents[0];

    /* ----------------------------------------------------
     * Status guard (CRITICAL)
     * -------------------------------------------------- */
    if (file.status !== "indexed") {
      return context.res.json(
        {
          success: false,
          error: "File is not ready for download",
        },
        409
      );
    }

    if (!file.storagePath) {
      return context.res.json(
        { success: false, error: "Missing storagePath" },
        500
      );
    }

    /* ----------------------------------------------------
     * S3 presigned download
     * -------------------------------------------------- */
    const s3 = new S3Client({
      endpoint: S3_ENDPOINT,
      region: S3_REGION ?? "us-east-1",
      credentials: {
        accessKeyId: S3_ACCESS_KEY_ID,
        secretAccessKey: S3_SECRET_ACCESS_KEY,
      },
      forcePathStyle: true,
    });

    const expiresIn = 60 * 60; // 1 hour

    const safeFilename = (file.name ?? fileId)
      .replace(/[^a-zA-Z0-9._-]/g, "_")
      .slice(0, 255);

    const command = new GetObjectCommand({
      Bucket: S3_BUCKET_NAME,
      Key: file.storagePath,
      ResponseContentDisposition: `attachment; filename="${safeFilename}"`,
      ResponseContentType: file.mimeType ?? "application/octet-stream",
    });

    const presignedUrl = await getSignedUrl(s3, command, {
      expiresIn,
    });

    return context.res.json({
      success: true,
      fileId,
      presignedUrl,
      expiresIn,
      metadata: {
        fileId,
        name: file.name,
        mimeType: file.mimeType,
      },
    });
  } catch (error) {
    console.error("presignDownload error:", error);
    return context.res.json(
      { success: false, error: error.message ?? "Internal server error" },
      500
    );
  }
}
