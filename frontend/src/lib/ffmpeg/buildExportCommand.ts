export function buildSmartVfFilter(
  width: number,
  height: number
) {
  return `
scale=${width}:${height}:force_original_aspect_ratio=decrease,
pad=${width}:${height}:(ow-iw)/2:(oh-ih)/2
`.replace(/\s+/g, " ");
}
