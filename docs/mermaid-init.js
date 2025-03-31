import mermaid from 'mermaid';

document.addEventListener('DOMContentLoaded', () => {
  mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    flowchart: {
      useMaxWidth: true,
      htmlLabels: true
    }
  });
}); 