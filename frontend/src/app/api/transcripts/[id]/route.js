export const runtime = "nodejs";

import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";
import Transcript from "@/models/Transcript";

export async function GET(req, { params }) {
  await clientPromise();

  const transcript = await Transcript.findById(params.id);

  if (!transcript) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  return NextResponse.json(transcript);
}

export async function DELETE(req, { params }) {
  await clientPromise();

  await Transcript.findByIdAndDelete(params.id);

  return NextResponse.json({ success: true });
}
