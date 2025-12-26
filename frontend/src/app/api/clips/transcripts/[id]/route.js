import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";
import { ObjectId } from "mongodb";

// ✅ GET transcript detail
export async function GET(req, { params }) {
  try {
    const { id } = await params; // 🔥 WAJIB await di App Router

    if (!id || !ObjectId.isValid(id)) {
      return NextResponse.json(
        { error: "Invalid transcript id" },
        { status: 400 }
      );
    }

    const client = await clientPromise;
    const db = client.db();

    const transcript = await db
      .collection("transcripts")
      .findOne({ _id: new ObjectId(id) });

    if (!transcript) {
      return NextResponse.json(
        { error: "Transcript not found" },
        { status: 404 }
      );
    }

    return NextResponse.json(transcript);
  } catch (err) {
    console.error("GET TRANSCRIPT ERROR:", err);
    return NextResponse.json(
      { error: "Failed to load transcript" },
      { status: 500 }
    );
  }
}

// ✅ DELETE transcript
export async function DELETE(req, { params }) {
  try {
    const { id } = await params; // 🔥 WAJIB await

    if (!id || !ObjectId.isValid(id)) {
      return NextResponse.json(
        { error: "Invalid transcript id" },
        { status: 400 }
      );
    }

    const client = await clientPromise;
    const db = client.db();

    await db.collection("transcripts").deleteOne({
      _id: new ObjectId(id),
    });

    // 🧹 hapus semua clip terkait transcript ini
    await db.collection("clips").deleteMany({
      transcriptId: new ObjectId(id),
    });

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error("DELETE TRANSCRIPT ERROR:", err);
    return NextResponse.json(
      { error: "Failed to delete transcript" },
      { status: 500 }
    );
  }
}
