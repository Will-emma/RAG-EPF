export interface TextSegment {
  text: string;
  bold: boolean;
}

// Le LLM répond en Markdown : on retire les lignes vides autour de la réponse,
// on remplace les puces "* " / "- " par "• ", on retire les marqueurs d'*italique*
// et on découpe le **gras** en segments
// (affichés via interpolation, donc échappés : pas d'innerHTML).
export function toSegments(text: string): TextSegment[] {
  const cleaned = text
    .trim()
    .replace(/^[ \t]*[*-][ \t]+/gm, '• ')
    .replace(/(^|[^*])\*(?![\s*])([^*\n]+?)(?<!\s)\*(?!\*)/g, '$1$2');
  return cleaned
    .split(/\*\*(.+?)\*\*/s)
    .map((part, index) => ({ text: part, bold: index % 2 === 1 }))
    .filter((segment) => segment.text !== '');
}

// Le backend renvoie des dates UTC sans fuseau ("2026-09-25T20:36:32") :
// sans le "Z", le navigateur les lirait comme des heures locales (décalage de 2 h).
export function parseApiDate(value: string): Date {
  return new Date(/[zZ]|[+-]\d{2}:?\d{2}$/.test(value) ? value : `${value}Z`);
}
