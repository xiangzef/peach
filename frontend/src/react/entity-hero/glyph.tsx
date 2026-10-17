/* 雪碧图（`web/index.html` 的 `#i-*` symbol）里的一枚字形，写法同遗留层 `icon()`：尺寸与描边
 * 由 `./entity-hero.css` 按位置给。横向的站点标识（JavDB 那枚是 326:111）viewBox 跟着 symbol
 * 的比例走，同 `src/core/index.ts` 的 `WIDE_ICONS`，槽位按高定宽。 */
const WIDE: Record<string, number> = { 'text-aa': 1.435, 'mark-javdb': 326 / 111 };

export function Glyph({ name }: { name: string }) {
  const ratio = WIDE[name];
  return (
    <svg viewBox={ratio ? `0 0 ${(24 * ratio).toFixed(2)} 24` : '0 0 24 24'} aria-hidden="true"
      data-glyph={ratio ? 'wide' : undefined}>
      <use href={`#i-${name}`} />
    </svg>
  );
}
