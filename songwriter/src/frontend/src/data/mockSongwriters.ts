// Types for Songwriter Data
export interface Credit {
  id: string;
  title: string;
  artist: {
    id: string;
    name: string;
  };
  year: number;
  role: 'Writer' | 'Producer' | 'Writer/Producer';
  album?: {
    id: string;
    title: string;
  };
}

export interface Award {
  id: string;
  name: string;
  year: number;
  category: string;
  type: 'Win' | 'Nomination';
  forWork?: string;
}

export interface Songwriter {
  id: string;
  name: string;
  bio?: string;
  photoUrl?: string;
  credits: Credit[];
  awards: Award[];
}

// Mock Data
export const mockSongwriters: Record<string, Songwriter> = {
  "1": {
    id: "1",
    name: "Max Martin",
    bio: "Karl Martin Sandberg (born 26 February 1971), known professionally as Max Martin, is a Swedish record producer and songwriter. He rose to prominence in the mid-1990s after making a string of hit singles such as Britney Spears's \"...Baby One More Time\" (1998), the Backstreet Boys' \"I Want It That Way\" (1999), and NSYNC's \"It's Gonna Be Me\" (2000).",
    photoUrl: "https://upload.wikimedia.org/wikipedia/commons/0/0c/Max_Martin_receives_the_Polar_Music_Prize_from_His_Majesty_the_King_of_Sweden%2C_2016_%28cropped%29.jpg",
    credits: [
      {
        id: "c1",
        title: "Shake It Off",
        artist: {
          id: "a1",
          name: "Taylor Swift"
        },
        year: 2014,
        role: "Writer/Producer",
        album: {
          id: "al1",
          title: "1989"
        }
      },
      {
        id: "c2",
        title: "Blinding Lights",
        artist: {
          id: "a2",
          name: "The Weeknd"
        },
        year: 2019,
        role: "Writer/Producer",
        album: {
          id: "al2",
          title: "After Hours"
        }
      },
      {
        id: "c3",
        title: "Can't Feel My Face",
        artist: {
          id: "a2",
          name: "The Weeknd"
        },
        year: 2015,
        role: "Writer/Producer",
        album: {
          id: "al3",
          title: "Beauty Behind the Madness"
        }
      },
      {
        id: "c4",
        title: "Blank Space",
        artist: {
          id: "a1",
          name: "Taylor Swift"
        },
        year: 2014,
        role: "Writer/Producer",
        album: {
          id: "al1",
          title: "1989"
        }
      },
      {
        id: "c5",
        title: "...Baby One More Time",
        artist: {
          id: "a3",
          name: "Britney Spears"
        },
        year: 1998,
        role: "Writer/Producer",
        album: {
          id: "al4",
          title: "...Baby One More Time"
        }
      }
    ],
    awards: [
      {
        id: "aw1",
        name: "Grammy Award",
        year: 2015,
        category: "Album of the Year",
        type: "Win",
        forWork: "1989 (Taylor Swift)"
      },
      {
        id: "aw2",
        name: "Grammy Award",
        year: 2016,
        category: "Producer of the Year, Non-Classical",
        type: "Win"
      },
      {
        id: "aw3",
        name: "Polar Music Prize",
        year: 2016,
        category: "Excellence in Music",
        type: "Win"
      }
    ]
  },
  "2": {
    id: "2",
    name: "Finneas O'Connell",
    bio: "Finneas Baird O'Connell (born July 30, 1997), known mononymously as Finneas, is an American singer-songwriter, record producer, and actor. He has written and produced music for various artists, including his younger sister, Billie Eilish.",
    photoUrl: "https://upload.wikimedia.org/wikipedia/commons/f/f3/Finneas_O%27Connell_2022.jpg",
    credits: [
      {
        id: "c6",
        title: "Bad Guy",
        artist: {
          id: "a4",
          name: "Billie Eilish"
        },
        year: 2019,
        role: "Writer/Producer",
        album: {
          id: "al5",
          title: "When We All Fall Asleep, Where Do We Go?"
        }
      },
      {
        id: "c7",
        title: "Everything I Wanted",
        artist: {
          id: "a4",
          name: "Billie Eilish"
        },
        year: 2019,
        role: "Writer/Producer"
      },
      {
        id: "c8",
        title: "No Time to Die",
        artist: {
          id: "a4",
          name: "Billie Eilish"
        },
        year: 2020,
        role: "Writer/Producer"
      }
    ],
    awards: [
      {
        id: "aw4",
        name: "Grammy Award",
        year: 2020,
        category: "Album of the Year",
        type: "Win",
        forWork: "When We All Fall Asleep, Where Do We Go? (Billie Eilish)"
      },
      {
        id: "aw5",
        name: "Grammy Award",
        year: 2020,
        category: "Producer of the Year, Non-Classical",
        type: "Win"
      },
      {
        id: "aw6",
        name: "Academy Award",
        year: 2022,
        category: "Best Original Song",
        type: "Win",
        forWork: "No Time to Die"
      }
    ]
  }
};

// Utility function to get a songwriter by ID
export function getSongwriterById(id: string): Songwriter | undefined {
  return mockSongwriters[id];
} 