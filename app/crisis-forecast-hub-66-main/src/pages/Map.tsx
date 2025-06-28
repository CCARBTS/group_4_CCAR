import React, { useEffect, useState } from 'react';

function HtmlEmbedder() {
  const [htmlContent, setHtmlContent] = useState('');

  useEffect(() => {
    fetch('exports/maps/test.html')
      .then((res) => res.text())
      .then((html) => {
        setHtmlContent(html);
      })
      .catch((err) => {
        console.error('Failed to load HTML:', err);
      });
  }, []);

  return (
    <div className="aspect-[16/9] bg-gray-100 flex items-center justify-center">
      <iframe
        src="/exports/maps/conflict_map.html"
        title="Conflict Map"
        className="w-full h-full border-0"
      />
    </div>
  );
}

export default HtmlEmbedder;