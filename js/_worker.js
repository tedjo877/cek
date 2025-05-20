export default {
  async fetch(request, env) {
    const { URLS } = env
    const url = new URL(request.url)

    if (request.method === "POST" && url.pathname === "/create") {
      const body = await request.json()
      const longUrl = body.url
      const customSlug = body.slug

      if (!longUrl) {
        return new Response(JSON.stringify({ error: "Missing URL" }), {
          status: 400,
          headers: { "Content-Type": "application/json" },
        })
      }

      const slug = customSlug || Math.random().toString(36).substring(2, 8)
      const exists = await URLS.get(slug)
      if (exists && !customSlug) {
        return new Response(JSON.stringify({ error: "Slug already exists" }), {
          status: 409,
          headers: { "Content-Type": "application/json" },
        })
      }

      await URLS.put(slug, longUrl)
      return new Response(JSON.stringify({ short: `${url.origin}/${slug}` }), {
        headers: { "Content-Type": "application/json" },
      })
    }

    if (request.method === "GET" && url.pathname === "/") {
      return new Response(htmlPage(url.origin), {
        headers: { "Content-Type": "text/html" },
      })
    }

    const path = url.pathname.slice(1)
    if (path) {
      const longUrl = await URLS.get(path)
      if (longUrl) return Response.redirect(longUrl, 302)
      return new Response("Short URL not found", { status: 404 })
    }

    return new Response("Invalid request", { status: 400 })
  },
}

function htmlPage(origin) {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>URL Shortener</title>
  <style>
    body { font-family: sans-serif; max-width: 500px; margin: 40px auto; padding: 0 20px; }
    input, button { padding: 8px; width: 100%; margin-top: 8px; box-sizing: border-box; }
    button { cursor: pointer; }
    #result { margin-top: 16px; }
    a { color: blue; }
    .copy-btn { margin-top: 8px; background: #eee; border: none; }
  </style>
</head>
<body>
  <h1>🔗 URL Shortener</h1>
  <form id="form">
    <input type="url" id="url" placeholder="Enter long URL" required />
    <input type="text" id="slug" placeholder="Custom slug (optional)" />
    <button type="submit">Shorten</button>
  </form>
  <div id="result"></div>
  <script>
    const form = document.getElementById("form");
    const result = document.getElementById("result");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const url = document.getElementById("url").value;
      const slug = document.getElementById("slug").value;
      const res = await fetch("/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, slug })
      });
      const data = await res.json();
      if (res.ok) {
        result.innerHTML = \`
          <p><strong>Short URL:</strong> 
            <a href="\${data.short}" target="_blank" id="short-url">\${data.short}</a>
          </p>
          <button class="copy-btn" onclick="copyToClipboard()">Salin</button>
        \`;
      } else {
        result.innerHTML = '<p style="color:red;">' + (data.error || res.statusText) + '</p>';
      }
    });

    function copyToClipboard() {
      const shortUrl = document.getElementById("short-url").textContent;
      navigator.clipboard.writeText(shortUrl).then(() => {
        alert("Link disalin!");
      }, () => {
        alert("Gagal menyalin.");
      });
    }
  </script>
</body>
</html>
`;
}
