import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function SongwriterNotFound() {
  return (
    <div className="container mx-auto py-24 px-4 text-center">
      <h1 className="text-4xl font-bold mb-6">Songwriter Not Found</h1>
      <p className="text-xl text-muted-foreground mb-8">
        Sorry, we couldn&apos;t find the songwriter you&apos;re looking for.
      </p>
      <Button asChild>
        <Link href="/">Return Home</Link>
      </Button>
    </div>
  );
} 