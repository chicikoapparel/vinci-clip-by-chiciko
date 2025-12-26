export const runtime = "nodejs";

import { NextResponse } from "next/server";

export async function POST(req) {
  const { url } = await req.json();

  if (!url) {
    return NextResponse.json(
      { error: "URL is required" },
      { status: 400 }
    );
  }

  return NextResponse.json({
    success: true,
    transcript: {
      _id: "import-url-stub-id",
      originalFilename: url,
      status: "processing",
      createdAt: new Date().toISOString(),
    },
  });
}
