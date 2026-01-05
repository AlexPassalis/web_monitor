interface ImageProps {
  src: string;
  alt: string;
  quality?: number;
  format?: "webp" | "avif" | "jpeg" | "png";
  className?: string;
  sizes?: string;
}

export default function Image({
  src,
  alt,
  quality = 75,
  format = "webp",
  className,
  sizes = "100vw",
}: ImageProps) {
  const hostname =
    window.location.hostname === "localhost" ? "localhost" : "alexpassalis.com"
  const baseUrl = `https://${hostname}/api/image/${src}`

  const buildUrl = (w: number) => {
    const params = new URLSearchParams()
    params.set("w", w.toString())

    if (quality !== 75) {
      params.set("q", quality.toString())
    }

    if (format !== "webp") {
      params.set("f", format)
    }

    return `${baseUrl}?${params.toString()}`
  }

  const responsiveWidths = [640, 750, 828, 1080, 1200, 1920, 2048, 3840]

  const srcSet = responsiveWidths
    .map((width) => {
      return `${buildUrl(width)} ${width}w`
    })
    .join(", ")

  return (
    <img
      src={buildUrl(1080)}
      srcSet={srcSet}
      alt={alt}
      loading="lazy"
      decoding="async"
      className={className}
      sizes={sizes}
    />
  )
}
