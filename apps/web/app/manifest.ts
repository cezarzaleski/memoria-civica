import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    background_color: "#f4efe4",
    display: "standalone",
    name: "Memoria Civica",
    short_name: "Memoria Civica",
    start_url: "/",
    theme_color: "#f4efe4"
  };
}
