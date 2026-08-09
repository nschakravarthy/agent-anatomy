// Admin-only tab. Which tabs render is decided in AppShell; anything that later
// reads or writes real data from here must also sit behind the backend's
// require_admin dependency, since hiding a tab is not a security boundary.
export default function ConfigurationPage() {
  return (
    <section className="placeholder-page">
      <h2>Configuration</h2>
      <p>Agent and system settings live here. Visible to admins only.</p>
    </section>
  );
}
