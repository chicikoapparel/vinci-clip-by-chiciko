import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";

export async function GET() {
  try {
    console.log("GET /api/clips/transcripts HIT");

    const client = await clientPromise;
    const db = client.db();

    const transcripts = await db
      .collection("transcripts")
      .find({})
      .sort({ createdAt: -1 })
      .limit(10)
      .toArray();

    return NextResponse.json(transcripts);
  } catch (error) {
    console.error("RECENT TRANSCRIPTS ERROR:", error);
    return NextResponse.json(
      { error: "Failed to fetch transcripts" },
      { status: 500 }
    );
  }
}
