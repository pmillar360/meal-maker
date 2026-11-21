import Image from 'next/image';
import { useState } from 'react';
import { FaUtensils } from 'react-icons/fa';

export default function RecipeImage({ src, title }: { src: string | null; title: string }) {
  const [failed, setFailed] = useState<string | null>(null);
  if (!src || src === failed) {
    return <div aria-hidden="true" className="grid h-full place-items-center bg-stone-100 text-stone-400"><FaUtensils size={32} /></div>;
  }
  return <Image src={src} alt={title} fill unoptimized className="object-cover" onError={() => setFailed(src)} />;
}
