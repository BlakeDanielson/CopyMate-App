import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';

import { getSongwriterById } from '@/data/mockSongwriters';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

// Define dynamic metadata
export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  const songwriter = getSongwriterById(params.id);
  
  if (!songwriter) {
    return {
      title: 'Songwriter Not Found',
    };
  }
  
  return {
    title: `${songwriter.name} | Songwriter Connect`,
    description: `View detailed information about ${songwriter.name}, including songs, credits, and awards.`,
  };
}

export default function SongwriterProfile({ params }: { params: { id: string } }) {
  const songwriter = getSongwriterById(params.id);
  
  if (!songwriter) {
    notFound();
  }
  
  return (
    <div className="container mx-auto py-8 px-4 md:px-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Songwriter Info Card */}
        <div className="md:col-span-1">
          <Card className="h-full">
            <CardHeader className="flex flex-col items-center">
              <Avatar className="h-36 w-36 mb-4">
                {songwriter.photoUrl ? (
                  <AvatarImage src={songwriter.photoUrl} alt={songwriter.name} />
                ) : null}
                <AvatarFallback className="text-3xl">{songwriter.name.substring(0, 2)}</AvatarFallback>
              </Avatar>
              <CardTitle className="text-2xl font-bold text-center">{songwriter.name}</CardTitle>
              <CardDescription className="text-center">Songwriter / Producer</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {songwriter.bio && (
                  <div>
                    <h3 className="text-lg font-medium mb-2">Biography</h3>
                    <p className="text-sm text-muted-foreground">{songwriter.bio}</p>
                  </div>
                )}
                
                {/* Stats Summary */}
                <div>
                  <h3 className="text-lg font-medium mb-2">Statistics</h3>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-muted rounded-lg p-3">
                      <div className="text-2xl font-bold">{songwriter.credits.length}</div>
                      <div className="text-xs text-muted-foreground">Credits</div>
                    </div>
                    <div className="bg-muted rounded-lg p-3">
                      <div className="text-2xl font-bold">{songwriter.awards.length}</div>
                      <div className="text-xs text-muted-foreground">Awards</div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Credits & Awards */}
        <div className="md:col-span-2">
          <Tabs defaultValue="credits" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="credits">Credits</TabsTrigger>
              <TabsTrigger value="awards">Awards</TabsTrigger>
            </TabsList>
            
            {/* Credits Tab */}
            <TabsContent value="credits" className="mt-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Songwriting & Production Credits</CardTitle>
                    <div className="text-sm text-muted-foreground">
                      Showing {songwriter.credits.length} credits
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {songwriter.credits.map((credit) => (
                      <div key={credit.id} className="p-4 border rounded-lg hover:bg-accent/50 transition-colors">
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 md:gap-4">
                          <div>
                            <Link 
                              href={`/songs/${credit.id}`} 
                              className="text-lg font-medium hover:underline"
                            >
                              {credit.title}
                            </Link>
                            <div className="flex flex-wrap items-center gap-2 mt-1">
                              <Link 
                                href={`/artists/${credit.artist.id}`}
                                className="text-sm text-muted-foreground hover:underline"
                              >
                                {credit.artist.name}
                              </Link>
                              {credit.album && (
                                <>
                                  <span className="text-sm text-muted-foreground">•</span>
                                  <Link 
                                    href={`/albums/${credit.album.id}`}
                                    className="text-sm text-muted-foreground hover:underline"
                                  >
                                    {credit.album.title}
                                  </Link>
                                </>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{credit.role}</Badge>
                            <Badge variant="secondary">{credit.year}</Badge>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            {/* Awards Tab */}
            <TabsContent value="awards" className="mt-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Awards & Nominations</CardTitle>
                    <div className="text-sm text-muted-foreground">
                      Showing {songwriter.awards.length} awards
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {songwriter.awards.map((award) => (
                      <div key={award.id} className="p-4 border rounded-lg hover:bg-accent/50 transition-colors">
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 md:gap-4">
                          <div>
                            <div className="flex items-center gap-2">
                              <h3 className="text-lg font-medium">{award.name}</h3>
                              <Badge 
                                className={award.type === 'Win' ? 'bg-green-600 hover:bg-green-700' : undefined}
                              >
                                {award.type}
                              </Badge>
                            </div>
                            <div className="text-sm text-muted-foreground mt-1">
                              {award.category}
                              {award.forWork && (
                                <span> • {award.forWork}</span>
                              )}
                            </div>
                          </div>
                          <Badge variant="outline">{award.year}</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
} 