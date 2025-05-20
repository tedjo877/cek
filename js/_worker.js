export default {
  async fetch(request, env) {
    const { URLS } = env;
    const url = new URL(request.url);

    if (request.method === "POST" && url.pathname === "/create") {
      const body = await request.json();
      const longUrl = body.url;
      const customSlug = body.slug;

      if (!longUrl) {
        return new Response(JSON.stringify({ error: "Missing URL" }), {
          status: 400,
          headers: { "Content-Type": "application/json" },
        });
      }

      const slug = customSlug || Math.random().toString(36).substring(2, 8);
      const exists = await URLS.get(slug);
      if (exists && !customSlug) {
        return new Response(JSON.stringify({ error: "Slug already exists" }), {
          status: 409,
          headers: { "Content-Type": "application/json" },
        });
      }

      await URLS.put(slug, longUrl);
      return new Response(JSON.stringify({ short: `${url.origin}/${slug}` }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    if (request.method === "GET" && url.pathname === "/") {
      return new Response(htmlPage(url.origin), {
        headers: { "Content-Type": "text/html" },
      });
    }

    const path = url.pathname.slice(1);
    if (path) {
      const longUrl = await URLS.get(path);
      if (longUrl) return Response.redirect(longUrl, 302);
      return new Response("Short URL not found", { status: 404 });
    }

    return new Response("Invalid request", { status: 400 });
  },
};

function htmlPage(origin) {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RESELLER TEMBAK KUOTA XL/AXIS PALING MURAH </title>
    <meta name="description" content="RESELLER TEMBAK KUOTA XL/AXIS PALING MURAH">
    <meta name="keywords" content="RESELLER TEMBAK KUOTA XL/AXIS PALING MURAH">
    <meta name="author" content="RESELLER TEMBAK KUOTA XL/AXIS PALING MURAH">
    <meta name="robots" content="RESELLER TEMBAK KUOTA XL/AXIS PALING MURAH">

    <!-- Open Graph Meta Tags untuk SEO Media Sosial -->
    <meta property="og:title" content="RESELLER TEMBAK KUOTA XL/AXIS PALING MURAH">
    <meta property="og:description" content="RESELLER TEMBAK KUOTA XL/AXIS PALING MURAH">
    <meta property="og:type" content="website">

    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="RESELLER TEMBAK KUOTA XL/AXIS PALING MURAH">
    <meta name="twitter:description" content="RESELLER TEMBAK KUOTA XL/AXIS PALING MURAH">
    <meta property="og:audio" content="URL-to-audio-if-any"/>
<meta property="og:video" content="URL-to-video-if-any"/>
<meta name="theme-color" content="#0f172a" media="(prefers-color-scheme: dark)"/>
<meta name="theme-color" content="#f8f9fa" media="(prefers-color-scheme: light)"/>
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<!-- QR Code Library -->
<script src="https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js"></script>
<!-- Add Inter font -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flag-icon-css/css/flag-icon.min.css">

  <style>
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background: linear-gradient(135deg, #1e3c72, #2a5298);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .container {
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    padding: 30px;
    max-width: 500px;
    width: 90%;
    box-sizing: border-box;
    transform: perspective(1000px);
    transition: transform 0.3s;
  }

  .container:hover {
    transform: perspective(1000px) rotateY(1deg) rotateX(1deg);
  }

  h1 {
    text-align: center;
    color: #1e3c72;
    margin-bottom: 24px;
    text-shadow: 1px 1px 2px #aaa;
  }

  input, button {
    width: 100%;
    padding: 12px;
    margin-top: 12px;
    border-radius: 8px;
    border: 1px solid #ccc;
    box-sizing: border-box;
    font-size: 16px;
    transition: all 0.2s;
  }

  input:focus {
    border-color: #2a5298;
    outline: none;
    box-shadow: 0 0 8px rgba(42, 82, 152, 0.4);
  }

  button {
    background: linear-gradient(135deg, #1e3c72, #2a5298);
    color: white;
    border: none;
    cursor: pointer;
    font-weight: bold;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
  }

  button:hover {
    background: linear-gradient(135deg, #2a5298, #1e3c72);
    transform: translateY(-2px);
  }

  #result {
    margin-top: 20px;
    text-align: center;
    word-wrap: break-word;
  }

  a {
    color: #2a5298;
    font-weight: bold;
    text-decoration: none;
  }

  a:hover {
    text-decoration: underline;
  }

  .copy-btn {
    margin-top: 10px;
    background: #eee;
    border: none;
    padding: 10px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.2s;
  }

  .copy-btn:hover {
    background: #ddd;
  }

  @media (max-width: 600px) {
    .container {
      padding: 20px;
    }

    input, button {
      font-size: 14px;
    }
  }
</style>

<body>
  <div class="container">
    <h1>🔗 URL Shortener</h1>
    <form id="form">
      <input type="url" id="url" placeholder="Enter long URL" required />
      <input type="text" id="slug" placeholder="Custom slug (optional)" />
      <button type="submit">Shorten</button>
    </form>
    <div id="result"></div>
  </div>
</body>


  <script>
    window.onload = () => {
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

      window.copyToClipboard = () => {
        const shortUrl = document.getElementById("short-url").textContent;
        navigator.clipboard.writeText(shortUrl).then(() => {
          alert("Link disalin!");
        }, () => {
          alert("Gagal menyalin.");
        });
      };
    };
  </script>
</body>
</html>
`;
}
