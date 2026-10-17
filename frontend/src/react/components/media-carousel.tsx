import { icon } from '@peach/legacy/core';
import { useLayoutEffect, useRef } from 'react';
import './media-carousel.css';
import { wireHorizontalScroller } from '../../ui-kit/scroll';

export interface CarouselMedia { index: number; label?: string; video?: boolean }

/** 关注与作品预览共用环形切换及可横向滚动的圆点。 */
export function MediaCarousel({ items, position, onSelect, below = false }: {
  items: readonly CarouselMedia[]; position: number; onSelect(index: number): void;
  below?: boolean;
}) {
  const root = useRef<HTMLDivElement>(null);
  const mixed = items.some(item => item.video);
  useLayoutEffect(() => {
    const wrapper = root.current;
    const strip = wrapper?.querySelector<HTMLElement>('[data-follow-image-dots]');
    const frame = wrapper?.closest<HTMLElement>('[data-stage-media]');
    if (!wrapper || !strip) return;
    const scroller = wireHorizontalScroller(strip, { drag: true });
    const measure = () => {
      const selected = strip.querySelector<HTMLElement>('[aria-current="true"]');
      if (selected && strip.clientWidth) {
        const item = selected.getBoundingClientRect(), bounds = strip.getBoundingClientRect();
        const padding = parseFloat(getComputedStyle(strip).paddingLeft);
        if (item.left < bounds.left + padding || item.right > bounds.right - padding)
          strip.scrollLeft += item.left - bounds.left - (strip.clientWidth - item.width) / 2;
      }
      if (below && frame?.clientWidth) {
        const media = [...frame.querySelectorAll<HTMLElement>('[data-jav-picture], [data-catalog-picture], .video-js')].find(node => node.offsetWidth > 0);
        const bounds = frame.getBoundingClientRect(), picture = media?.getBoundingClientRect();
        const center = picture ? picture.y - bounds.y + picture.height / 2 : (wrapper.getBoundingClientRect().y - bounds.y) / 2;
        wrapper.style.setProperty('--media-arrow-top', `${Math.max(0, center)}px`);
      }
      scroller?.update();
    };
    const observer = new ResizeObserver(measure);
    observer.observe(strip);
    if (frame) observer.observe(frame);
    measure();
    return () => { observer.disconnect(); scroller?.destroy() };
  }, [items.length, position, below]);
  if (items.length < 2) return null;
  const step = (delta: number) => onSelect(items[(position + delta + items.length) % items.length]!.index);
  const unit = mixed ? '项媒体' : '张图片';
  const indicator = (item: CarouselMedia, index: number) => <button key={item.index} type="button" data-follow-image-item={item.index}
    data-carousel-video={item.video ? '' : undefined} aria-current={index === position ? 'true' : 'false'}
    aria-label={item.label || `第 ${index + 1} 张，共 ${items.length} 张`} title={item.label || `第 ${index + 1} 张`}
    onClick={() => onSelect(item.index)}>{item.video ? <span dangerouslySetInnerHTML={{ __html: icon('play') }} /> : null}</button>;
  return <div ref={root} data-media-carousel="" data-carousel-below={below ? '' : undefined}
    data-carousel-video-active={items[position]?.video ? '' : undefined}>
    {!items[position]?.video ? <><button type="button" data-follow-image-step="-1" data-follow-image-arrow="prev" aria-label={mixed ? '上一项媒体' : '上一张图片'} title="上一张"
      onClick={() => step(-1)} dangerouslySetInnerHTML={{ __html: icon('chevron-left') }} />
    <button type="button" data-follow-image-step="1" data-follow-image-arrow="next" aria-label={mixed ? '下一项媒体' : '下一张图片'} title="下一张"
      onClick={() => step(1)} dangerouslySetInnerHTML={{ __html: icon('chevron-right') }} /></> : null}
    <div data-media-indicator=""><div data-follow-image-dots="" role="group" aria-label={`${items.length} ${unit}`}>
      {items.map((item, index) => indicator(item, index))}
    </div></div>
  </div>;
}
