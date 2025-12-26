export const runtime = "nodejs";

import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";
import Transcript from "@/models/Transcript";

export async function POST(req) {
  await clientPromise();
  const { url } = await req.json();

  const doc = await Transcript.create({
    originalFilename: url,
    status: "processing",
  });

  return NextResponse.json(doc);
}
