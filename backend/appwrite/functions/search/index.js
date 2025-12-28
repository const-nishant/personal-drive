// Search Function
// Handles search queries and coordinates with semantic service
// Returns complete results with file metadata

import { Client, Databases, Query } from "node-appwrite";

/**
 * @param {object} context - The Appwrite function context
 * @param {object} req - The request object
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
      // Fallback: try to parse from body string
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

    const { query, k = 5, userId: bodyUserId } = requestBody;

    // Get user ID from request
    const userId = req?.headers?.["x-appwrite-user-id"] || bodyUserId;
    if (!userId) {
      return context.res.json(
        {
          success: false,
          error: "User authentication required",
        },
        401
      );
    }

    // Validate query
    if (!query || typeof query !== "string" || !query.trim()) {
      return context.res.json(
        {
          success: false,
          error: "Search query is required",
        },
        400
      );
    }

    // Validate query length (max 500 chars)
    const sanitizedQuery = query.trim().substring(0, 500);
    if (sanitizedQuery.length === 0) {
      return context.res.json(
        {
          success: false,
          error: "Search query cannot be empty",
        },
        400
      );
    }

    // Validate k (number of results)
    const numResults = parseInt(k);
    if (isNaN(numResults) || numResults <= 0 || numResults > 100) {
      return context.res.json(
        {
          success: false,
          error: "k must be a positive integer between 1 and 100",
        },
        400
      );
    }

    // Call semantic service
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

    let fileIds = [];
    try {
      const searchResponse = await fetch(`${semanticServiceUrl}/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": semanticServiceApiKey || "",
        },
        body: JSON.stringify({
          query: sanitizedQuery,
          k: numResults,
        }),
      });

      if (!searchResponse.ok) {
        const errorData = await searchResponse
          .json()
          .catch(() => ({ detail: "Unknown error" }));
        throw new Error(
          errorData.detail || `Semantic service error: ${searchResponse.status}`
        );
      }

      const searchResult = await searchResponse.json();
      fileIds = searchResult.file_ids || [];
    } catch (error) {
      console.error("Error calling semantic service:", error);
      return context.res.json(
        {
          success: false,
          error: `Search failed: ${error.message}`,
        },
        500
      );
    }

    // If no results, return empty array
    if (fileIds.length === 0) {
      return context.res.json({
        success: true,
        query: sanitizedQuery,
        results: [],
        count: 0,
      });
    }

    // Fetch file metadata from database for each fileId
    const collectionId = context.env.FILES_COLLECTION_ID || "files";
    const databaseId = context.env.APPWRITE_DATABASE_ID || "default";

    const results = [];

    for (const fileId of fileIds) {
      try {
        // Query by fileId and userId (ensure user owns the file)
        const documents = await databases.listDocuments(
          databaseId,
          collectionId,
          [Query.equal("fileId", fileId), Query.equal("userId", userId)],
          1 // Limit to 1 result
        );

        if (documents.documents.length > 0) {
          const doc = documents.documents[0];

          // Only include indexed files
          if (doc.indexed === true && doc.status === "indexed") {
            results.push({
              fileId: doc.fileId,
              name: doc.name,
              mimeType: doc.mimeType,
              size: doc.size,
              storagePath: doc.storagePath,
              createdAt: doc.createdAt,
              description: doc.description || "",
              tags: doc.tags || [],
              folderId: doc.folderId || null,
            });
          }
        }
      } catch (error) {
        console.error(`Error fetching metadata for fileId ${fileId}:`, error);
        // Continue with other files
      }
    }

    return context.res.json({
      success: true,
      query: sanitizedQuery,
      results,
      count: results.length,
    });
  } catch (error) {
    console.error("Error in search function:", error);
    return context.res.json(
      {
        success: false,
        error: error.message || "Internal server error",
      },
      500
    );
  }
}
