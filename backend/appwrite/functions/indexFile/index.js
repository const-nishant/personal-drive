import { Client, Databases, Query } from "node-appwrite";
import {
  S3Client,
  GetObjectCommand,
  HeadObjectCommand,
} from "@aws-sdk/client-s3";
import crypto from "crypto";

export default async function indexFile(context, req) {
  try {
    const request = req ?? context.req;

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

      SEMANTIC_SERVICE_URL,
      SEMANTIC_SERVICE_API_KEY,
    } = process.env;

    if (
      !APPWRITE_FUNCTION_ENDPOINT ||
      !APPWRITE_FUNCTION_PROJECT_ID ||
      !APPWRITE_FUNCTION_API_KEY ||
      !APPWRITE_DATABASE_ID ||
      !FILES_COLLECTION_ID ||
      !S3_ENDPOINT ||
      !S3_ACCESS_KEY_ID ||
      !S3_SECRET_ACCESS_KEY ||
      !S3_BUCKET_NAME ||
      !SEMANTIC_SERVICE_URL
    ) {
      return context.res.json(
        { success: false, error: "Server misconfigured" },
        500
      );
    }

    let body = request.bodyJson ?? {};
    if (typeof body?.data === "string") body = JSON.parse(body.data);
    if (typeof body?.data === "object") body = body.data;

    const { fileId } = body;
    if (!fileId) {
      return context.res.json(
        { success: false, error: "fileId required" },
        400
      );
    }

    const client = new Client()
      .setEndpoint(APPWRITE_FUNCTION_ENDPOINT)
      .setProject(APPWRITE_FUNCTION_PROJECT_ID)
      .setKey(APPWRITE_FUNCTION_API_KEY);

    const databases = new Databases(client);

    const docs = await databases.listDocuments(
      APPWRITE_DATABASE_ID,
      FILES_COLLECTION_ID,
      [Query.equal("fileId", fileId)]
    );

    if (docs.documents.length === 0) {
      return context.res.json({ success: false, error: "File not found" }, 404);
    }

    const file = docs.documents[0];
    if (file.indexed === true) return;

    const s3 = new S3Client({
      endpoint: S3_ENDPOINT,
      region: S3_REGION ?? "us-east-1",
      credentials: {
        accessKeyId: S3_ACCESS_KEY_ID,
        secretAccessKey: S3_SECRET_ACCESS_KEY,
      },
      forcePathStyle: true,
    });

    /* ---- VERIFY UPLOAD EXISTS ---- */
    try {
      await s3.send(
        new HeadObjectCommand({
          Bucket: S3_BUCKET_NAME,
          Key: file.storagePath,
        })
      );
    } catch {
      await databases.updateDocument(
        APPWRITE_DATABASE_ID,
        FILES_COLLECTION_ID,
        file.$id,
        { status: "failed" }
      );
      return;
    }

    /* ---- DOWNLOAD ---- */
    const obj = await s3.send(
      new GetObjectCommand({
        Bucket: S3_BUCKET_NAME,
        Key: file.storagePath,
      })
    );

    const chunks = [];
    for await (const c of obj.Body) chunks.push(c);
    const buffer = Buffer.concat(chunks);

    /* ---- HASH ---- */
    const hash = crypto.createHash("sha256").update(buffer).digest("hex");

    const dup = await databases.listDocuments(
      APPWRITE_DATABASE_ID,
      FILES_COLLECTION_ID,
      [Query.equal("hash", hash), Query.equal("userId", file.userId)]
    );

    if (dup.documents.length > 0 && dup.documents[0].fileId !== fileId) {
      await databases.updateDocument(
        APPWRITE_DATABASE_ID,
        FILES_COLLECTION_ID,
        file.$id,
        {
          hash,
          indexed: true,
          status: "indexed",
          storagePath: dup.documents[0].storagePath,
        }
      );
      return;
    }

    /* ---- TEXT EXTRACTION ---- */
    let text = "";
    try {
      if (file.mimeType === "application/pdf") {
        const pdf = await import("pdf-parse");
        text = (await pdf.default(buffer)).text;
      } else if (file.mimeType === "text/plain") {
        text = buffer.toString("utf-8");
      } else {
        text = file.name;
      }
    } catch {
      text = file.name;
    }

    text = text.slice(0, 100_000);

    /* ---- INDEX ---- */
    const res = await fetch(`${SEMANTIC_SERVICE_URL}/index`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(SEMANTIC_SERVICE_API_KEY && {
          "X-API-Key": SEMANTIC_SERVICE_API_KEY,
        }),
      },
      body: JSON.stringify({ file_id: fileId, text }),
    });

    if (!res.ok) {
      await databases.updateDocument(
        APPWRITE_DATABASE_ID,
        FILES_COLLECTION_ID,
        file.$id,
        { hash, status: "failed" }
      );
      return;
    }

    const out = await res.json();

    await databases.updateDocument(
      APPWRITE_DATABASE_ID,
      FILES_COLLECTION_ID,
      file.$id,
      {
        hash,
        indexed: true,
        status: "indexed",
        vectorId: out.vectorId ?? null,
      }
    );
  } catch (err) {
    console.error("indexFile:", err);
  }
}
