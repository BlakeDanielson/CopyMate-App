import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';

import { mockSongwriters } from '@/data/mockSongwriters';

export default function Home() {
  // Convert the mockSongwriters object to an array
  const songwritersList = Object.values(mockSongwriters);

  return (
    <div className="container mx-auto py-12 px-4">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">Songwriter Connect</h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Your source for detailed information about mainstream pop songwriters, their credits, and achievements.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {songwritersList.map((songwriter) => (
          <Card key={songwriter.id} className="flex flex-col">
            <CardHeader>
              <CardTitle>{songwriter.name}</CardTitle>
              <CardDescription className="line-clamp-2">
                {songwriter.credits.length} credits • {songwriter.awards.length} awards
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-grow">
              <p className="text-sm text-muted-foreground line-clamp-4">
                {songwriter.bio}
              </p>
            </CardContent>
            <CardFooter>
              <Button asChild className="w-full">
                <Link href={`/songwriters/${songwriter.id}`}>View Profile</Link>
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      <div className="mt-20 max-w-2xl mx-auto text-center">
        <h2 className="text-2xl font-bold mb-4">About Songwriter Connect</h2>
        <p className="text-muted-foreground mb-6">
          Songwriter Connect is a high-accuracy information portal focused on mainstream pop songwriters active from 2000 onwards.
          Our goal is to provide detailed profiles including comprehensive credits, awards, and production information.
        </p>
        <div className="flex justify-center gap-4">
          <Button variant="outline" asChild>
            <Link href="/about">Learn More</Link>
          </Button>
          <Button asChild>
            <Link href="/songwriters">All Songwriters</Link>
          </Button>
        </div>
      </div>
    </div>
  );
} 