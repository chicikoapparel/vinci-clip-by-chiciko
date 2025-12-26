export const runtime = "nodejs";

import { NextResponse } from "next/server";

export async function GET(req, context) {
  const { clipId } = await context.params; // ✅ WAJIB await

  const encoder = new TextEncoder();

  let progress = 0;

  const stream = new ReadableStream({
    start(controller) {
      const interval = setInterval(() => {
        progress += 5;

        controller.enqueue(
          encoder.encode(`data: ${progress}\n\n`)
        );

        if (progress >= 100) {
          clearInterval(interval);
          controller.close();
        }
      }, 500);
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
