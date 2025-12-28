import { Client, ID, Databases } from "node-appwrite";
import {
  S3Client,
  PutObjectCommand,
  CreateMultipartUploadCommand,
  UploadPartCommand,
} from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

export default async function presignUpload(context, req) {
  try {
    const request = req ?? context.req;
    if (!request) {
      return context.res.json(
        { success: false, error: "Invalid context" },
        400
      );
    }

    /* ---------------- ENV ---------------- */
    const {
      APPWRITE_FUNCTION_ENDPOINT,
      APPWRITE_FUNCTION_PROJECT_ID,
      APPWRITE_FUNCTION_API_KEY,
      APPWRITE_DATABASE_ID,
      FILES_COLLECTION_ID,

      S3_ENDPOINT,
      S3_ACCESS_KEY_ID,
      S3_SECRET_ACCESS_KEY,
      S3_BUCKET_NAME,
      S3_REGION,

      MAX_FILE_SIZE = "1073741824",
      ALLOWED_MIME_TYPES,
    } = process.env;

    const requiredEnvVars = [
      APPWRITE_FUNCTION_ENDPOINT,
      APPWRITE_FUNCTION_PROJECT_ID,
      APPWRITE_FUNCTION_API_KEY,
      APPWRITE_DATABASE_ID,
      FILES_COLLECTION_ID,
      S3_ENDPOINT,
      S3_ACCESS_KEY_ID,
      S3_SECRET_ACCESS_KEY,
      S3_BUCKET_NAME,
    ];

    if (requiredEnvVars.some((v) => !v)) {
      return context.res.json(
        { success: false, error: "Server misconfigured" },
        500
      );
    }

    context.log("STEP 0: function entered");

    // Debug: Log all available request properties
    const requestKeys = Object.keys(request || {});
    context.log("STEP 0: request object inspection", {
      hasRequest: !!request,
      requestKeys: requestKeys,
      method: request?.method,
      url: request?.url,
      headers: request?.headers ? Object.keys(request.headers) : [],
      hasBodyRaw: "bodyRaw" in (request || {}),
      hasBodyJson: "bodyJson" in (request || {}),
      hasBody: "body" in (request || {}),
      // Try to access body directly if it exists
      bodyType: typeof request?.body,
      bodyValue: request?.body ? String(request.body).substring(0, 200) : null,
    });

    /* ---------------- REQUEST BODY (SAFE + APPWRITE-COMPATIBLE) ---------------- */
    // Try bodyRaw first (safer - doesn't auto-parse), then fallback to bodyJson
    let body = {};
    let rawBody = null;

    // First, try to get raw body string - try multiple ways
    try {
      rawBody = request.bodyRaw;
      context.log("STEP 0: bodyRaw accessed", {
        type: typeof rawBody,
        length: rawBody?.length,
        preview: rawBody?.substring(0, 200),
      });
    } catch (e) {
      context.log("STEP 0: bodyRaw access failed", { error: e.message });
      // Try request.body as fallback
      try {
        if (request.body && typeof request.body === "string") {
          rawBody = request.body;
          context.log("STEP 0: got body from request.body", {
            length: rawBody.length,
            preview: rawBody.substring(0, 200),
          });
        }
      } catch (e2) {
        context.log("STEP 0: request.body access also failed", {
          error: e2.message,
        });
      }
    }

    // If we have raw body, parse it manually
    if (rawBody && typeof rawBody === "string" && rawBody.trim().length > 0) {
      try {
        body = JSON.parse(rawBody);
        context.log("STEP 0: parsed body from bodyRaw", {
          bodyKeys: Object.keys(body),
        });
      } catch (parseError) {
        context.log("STEP 0: failed to parse bodyRaw", {
          error: parseError.message,
          bodyPreview: rawBody.substring(0, 200),
        });
        return context.res.json(
          {
            success: false,
            error: `Invalid JSON in request body: ${parseError.message}`,
          },
          400
        );
      }
    } else {
      // bodyRaw is empty - this means the HTTP request body wasn't sent
      // When using Appwrite execution API via REST, body must be wrapped in { data: "..." }
      context.log("STEP 0: bodyRaw is empty - request body not received", {
        bodyRawLength: rawBody?.length || 0,
        bodyRawType: typeof rawBody,
      });
      return context.res.json(
        {
          success: false,
          error:
            "Request body is empty. When using Appwrite execution API, " +
            "the body must be sent as: " +
            '{"data":"{\\"name\\":\\"test.txt\\",\\"size\\":25,\\"mimeType\\":\\"text/plain\\"}"} ' +
            "(Note: the inner JSON must be stringified). " +
            "In Postman: Body tab → raw → JSON → Use the format above.",
        },
        400
      );
    }

    // Handle Appwrite execution API format: body may be wrapped in { data: ... }
    if (typeof body?.data === "string") {
      // Only parse if the string is not empty
      if (body.data.trim().length === 0) {
        context.log("STEP 0: body.data is empty string");
        return context.res.json(
          {
            success: false,
            error: "Request body is empty or invalid",
          },
          400
        );
      }
      try {
        body = JSON.parse(body.data);
      } catch (parseError) {
        context.log("STEP 0: failed to parse body.data string", {
          error: parseError.message,
          bodyData: body.data?.substring(0, 100),
        });
        return context.res.json(
          {
            success: false,
            error: `Invalid JSON in body.data: ${parseError.message}`,
          },
          400
        );
      }
    } else if (typeof body?.data === "object" && body.data !== null) {
      body = body.data;
    } else if (Object.keys(body).length === 0) {
      // Body is empty object - no data provided
      context.log("STEP 0: body is empty after parsing");
      return context.res.json(
        {
          success: false,
          error: "Request body is required",
        },
        400
      );
    }

    context.log("STEP 1: body parsed");

    const {
      name,
      size,
      mimeType,
      folderId = null,
      description = null,
      tags = null,
      uploadMode = "single",
      parts = 0,
      userId: bodyUserId,
    } = body;

    const userId =
      request.headers?.["x-appwrite-user-id"] ??
      request.headers?.["X-Appwrite-User-Id"] ??
      bodyUserId;

    if (
      !userId ||
      !name ||
      !mimeType ||
      typeof size !== "number" ||
      size <= 0
    ) {
      return context.res.json(
        { success: false, error: "Invalid request payload" },
        400
      );
    }

    if (size > Number(MAX_FILE_SIZE)) {
      return context.res.json({ success: false, error: "File too large" }, 400);
    }

    const allowedTypes = (
      ALLOWED_MIME_TYPES ??
      "application/pdf,text/plain,image/jpeg,image/png,image/webp,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ).split(",");

    if (!allowedTypes.includes(mimeType)) {
      return context.res.json(
        { success: false, error: "MIME type not allowed" },
        400
      );
    }

    const sanitizedName = name.replace(/[^a-zA-Z0-9._-]/g, "_").slice(0, 255);
    const fileId = ID.unique();
    const now = new Date();

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");

    const storagePath = mimeType.startsWith("image/")
      ? `photos/${year}/${month}/${fileId}_${sanitizedName}`
      : `documents/${userId}/${fileId}_${sanitizedName}`;

    /* ---------------- S3 ---------------- */
    context.log("STEP 2: creating S3 client");

    const s3 = new S3Client({
      endpoint: S3_ENDPOINT,
      region: S3_REGION || "us-east-1",
      credentials: {
        accessKeyId: S3_ACCESS_KEY_ID,
        secretAccessKey: S3_SECRET_ACCESS_KEY,
      },
      forcePathStyle: true,
    });

    let upload;

    if (uploadMode === "multipart") {
      if (!parts || parts < 1) {
        return context.res.json(
          { success: false, error: "Invalid multipart parts" },
          400
        );
      }

      const create = await s3.send(
        new CreateMultipartUploadCommand({
          Bucket: S3_BUCKET_NAME,
          Key: storagePath,
          ContentType: mimeType,
        })
      );

      const urls = await Promise.all(
        Array.from({ length: parts }).map((_, i) =>
          getSignedUrl(
            s3,
            new UploadPartCommand({
              Bucket: S3_BUCKET_NAME,
              Key: storagePath,
              UploadId: create.UploadId,
              PartNumber: i + 1,
            }),
            { expiresIn: 900 }
          )
        )
      );

      upload = {
        mode: "multipart",
        uploadId: create.UploadId,
        parts: urls.map((url, i) => ({
          partNumber: i + 1,
          url,
        })),
      };
    } else {
      upload = {
        mode: "single",
        url: await getSignedUrl(
          s3,
          new PutObjectCommand({
            Bucket: S3_BUCKET_NAME,
            Key: storagePath,
            ContentType: mimeType,
          }),
          { expiresIn: 900 }
        ),
      };
    }

    /* ---------------- DATABASE ---------------- */
    context.log("STEP 3: creating database record");

    const client = new Client()
      .setEndpoint(APPWRITE_FUNCTION_ENDPOINT)
      .setProject(APPWRITE_FUNCTION_PROJECT_ID)
      .setKey(APPWRITE_FUNCTION_API_KEY);

    const databases = new Databases(client);

    await databases.createDocument(
      APPWRITE_DATABASE_ID,
      FILES_COLLECTION_ID,
      ID.unique(),
      {
        fileId,
        userId,
        name: sanitizedName,
        size,
        mimeType,
        folderId,
        description,
        tags,
        indexed: false,
        vectorId: null,
        hash: null,
        storagePath,
        createdAt: now.toISOString(),
        status: "pending",
      }
    );

    context.log("STEP 4: success");

    return context.res.json({
      success: true,
      fileId,
      upload,
    });
  } catch (err) {
    context.error("presignUpload failed", err);
    return context.res.json(
      { success: false, error: err.message || "Internal error" },
      500
    );
  }
}
