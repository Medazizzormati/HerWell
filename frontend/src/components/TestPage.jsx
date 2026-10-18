// Simple test component for pages that appear empty
export function TestPage({ title }) {
  return (
    <div style={{ padding: '2rem' }}>
      <h1>{title}</h1>
      <p>Cette page fonctionne correctement.</p>
    </div>
  );
}
