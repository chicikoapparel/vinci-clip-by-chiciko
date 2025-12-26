import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";

export async function GET() {
  try {
    const client = await clientPromise;
    const db = client.db();

    const data = await db
      .collection("transcripts")
      .find({})
      .sort({ createdAt: -1 })
      .toArray();

    return NextResponse.json(data);
  } catch (error) {
    console.error("GET TRANSCRIPTS ERROR:", error);
    return NextResponse.json(
      { error: "Failed to fetch transcripts" },
      { status: 500 }
    );
  }
}
