import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";
import { ObjectId } from "mongodb";

/**
 * DELETE /api/clips/:clipId
 */
export async function DELETE(req, { params }) {
  try {
    const { clipId } = await params;

    if (!clipId || !ObjectId.isValid(clipId)) {
      return NextResponse.json(
        { error: "Invalid clipId" },
        { status: 400 }
      );
    }

    const client = await clientPromise;
    const db = client.db();

    await db.collection("clips").deleteOne({
      _id: new ObjectId(clipId),
    });

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error("DELETE CLIP ERROR:", err);
    return NextResponse.json(
      { error: "Failed to delete clip" },
      { status: 500 }
    );
  }
}

/**
 * PATCH /api/clips/:clipId
 * rename, tag, export format
 */
export async function PATCH(req, { params }) {
  try {
    const { clipId } = await params;

    if (!clipId || !ObjectId.isValid(clipId)) {
      return NextResponse.json(
        { error: "Invalid clipId" },
        { status: 400 }
      );
    }

    const body = await req.json();
    const { title, tags, exportFormat } = body;

    const client = await clientPromise;
    const db = client.db();

    await db.collection("clips").updateOne(
      { _id: new ObjectId(clipId) },
      {
        $set: {
          title: typeof title === "string" ? title : "",
          tags: Array.isArray(tags) ? tags : [],
          exportFormat: ["horizontal", "vertical", "square"].includes(
            exportFormat
          )
            ? exportFormat
            : "horizontal",
          updatedAt: new Date(),
        },
      }
    );

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error("PATCH CLIP ERROR:", err);
    return NextResponse.json(
      { error: "Failed to update clip" },
      { status: 500 }
    );
  }
}
