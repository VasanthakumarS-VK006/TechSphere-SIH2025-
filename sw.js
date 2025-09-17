self.addEventListener("install", event => {
  console.log("✅ Service Worker installed");
});

// Activate event
self.addEventListener("activate", event => {
  console.log("✅ Service Worker activated");
});

// Fetch event (optional: offline fallback later)
self.addEventListener("fetch", event => {
  console.log("Fetching:", event.request.url);
});
