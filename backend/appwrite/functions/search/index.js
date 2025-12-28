import { Client, Databases, Query } from "node-appwrite";

/**
 * Appwrite Function: search
 * - Performs semantic search
 * - Returns indexed files owned by the user
 */
export default async function search(context, req) {
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
      SEMANTIC_SERVICE_URL,
      SEMANTIC_SERVICE_API_KEY,
    } = context.env;

    if (
      !APPWRITE_FUNCTION_ENDPOINT ||
      !APPWRITE_FUNCTION_PROJECT_ID ||
      !APPWRITE_FUNCTION_API_KEY ||
      !SEMANTIC_SERVICE_URL
    ) {
      return context.res.json(
        { success: false, error: "Server configuration incomplete" },
        500
      );
    }

    /* ----------------------------------------------------
     * Request parsing
     * -------------------------------------------------- */
    let body = request.bodyJson ?? {};
    if (typeof body?.data === "string") body = JSON.parse(body.data);
    if (typeof body?.data === "object") body = body.data;

    const { query, k = 5, userId: bodyUserId } = body;
    const userId = request.headers?.["x-appwrite-user-id"] ?? bodyUserId;

    if (!userId) {
      return context.res.json(
        { success: false, error: "Authentication required" },
        401
      );
    }

    if (!query || typeof query !== "string" || !query.trim()) {
      return context.res.json(
        { success: false, error: "Search query is required" },
        400
      );
    }

    const sanitizedQuery = query.trim().slice(0, 500);

    const limit = Number(k);
    if (!Number.isInteger(limit) || limit < 1 || limit > 100) {
      return context.res.json(
        { success: false, error: "k must be between 1 and 100" },
        400
      );
    }

    /* ----------------------------------------------------
     * Semantic search (UNTRUSTED input)
     * -------------------------------------------------- */
    const searchResponse = await fetch(`${SEMANTIC_SERVICE_URL}/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(SEMANTIC_SERVICE_API_KEY && {
          "X-API-Key": SEMANTIC_SERVICE_API_KEY,
        }),
      },
      body: JSON.stringify({
        query: sanitizedQuery,
        k: limit,
      }),
    });

    if (!searchResponse.ok) {
      throw new Error(`Semantic service error (${searchResponse.status})`);
    }

    const semanticResult = await searchResponse.json();
    const fileIds = Array.isArray(semanticResult.file_ids)
      ? semanticResult.file_ids
      : [];

    if (fileIds.length === 0) {
      return context.res.json({
        success: true,
        query: sanitizedQuery,
        results: [],
        count: 0,
      });
    }

    /* ----------------------------------------------------
     * Fetch metadata in ONE query
     * -------------------------------------------------- */
    const client = new Client()
      .setEndpoint(APPWRITE_FUNCTION_ENDPOINT)
      .setProject(APPWRITE_FUNCTION_PROJECT_ID)
      .setKey(APPWRITE_FUNCTION_API_KEY);

    const databases = new Databases(client);

    const docs = await databases.listDocuments(
      APPWRITE_DATABASE_ID,
      FILES_COLLECTION_ID,
      [
        Query.equal("fileId", fileIds),
        Query.equal("userId", userId),
        Query.equal("indexed", true),
        Query.equal("status", "indexed"),
      ],
      limit
    );

    const results = docs.documents.map((doc) => ({
      fileId: doc.fileId,
      name: doc.name,
      mimeType: doc.mimeType,
      size: doc.size,
      createdAt: doc.createdAt,
      description: doc.description ?? "",
      tags: doc.tags ?? [],
      folderId: doc.folderId ?? null,
    }));

    return context.res.json({
      success: true,
      query: sanitizedQuery,
      results,
      count: results.length,
    });
  } catch (error) {
    console.error("search error:", error);
    return context.res.json(
      { success: false, error: error.message ?? "Internal server error" },
      500
    );
  }
}
