import { useState } from 'react';
import { coverUrl } from '@peach/card-art';
import { Button } from '@/components/base/buttons/button';
import { Note } from '../components/note';
import { SourcePicture } from '../components/source-picture';
import type { DetailItem } from './item-detail';

/** 馆藏官方样张使用现有按需图片缓存。 */
export function CatalogPicture({ item, image, source = false }: { item: DetailItem; image: number; source?: boolean }) {
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  if (source && image > 0 && item.code) return <SourcePicture item={{ code: item.code, has_cover: false, source_image: true }} image={String(image - 1)} />;
  const src = image < 0 ? coverUrl(item, true)
    : `/sample-image?code=${encodeURIComponent(item.code || '')}&n=${image}`;
  if (failed) return <Note tone="neutral" action={<Button variant="secondary"
    onClick={() => { setFailed(false); setAttempt(value => value + 1) }}>重试</Button>}>预览未取得</Note>;
  return <img key={attempt} data-catalog-picture="" src={src} alt={image < 0 ? `${item.code} 封面` : `${item.code} 预览 ${image}`}
    onError={() => setFailed(true)} />;
}
