import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";
import { ObjectId } from "mongodb";

export async function GET(req, { params }) {
  try {
    const { id } = await params;

    if (!id || !ObjectId.isValid(id)) {
      return NextResponse.json([], { status: 200 });
    }

    const client = await clientPromise;
    const db = client.db();

    const clips = await db
      .collection("clips")
      .find({ transcriptId: new ObjectId(id) })
      .sort({ createdAt: -1 })
      .toArray();

    return NextResponse.json(clips);
  } catch (err) {
    console.error("GET CLIPS BY TRANSCRIPT ERROR:", err);
    return NextResponse.json([], { status: 500 });
  }
}
