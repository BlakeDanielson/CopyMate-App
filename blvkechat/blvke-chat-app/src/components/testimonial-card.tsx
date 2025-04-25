interface TestimonialCardProps {
  quote: string
  author: string
  role: string
  avatarUrl: string
}

export default function TestimonialCard({ quote, author, role, avatarUrl }: TestimonialCardProps) {
  return (
    <div className="flex flex-col p-6 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
      <div className="flex-1">
        <svg className="h-8 w-8 text-violet-400 mb-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
        </svg>
        <p className="text-gray-700 mb-4">{quote}</p>
      </div>
      <div className="flex items-center mt-4">
        <img src={avatarUrl || "/placeholder.svg"} alt={author} className="h-10 w-10 rounded-full mr-3 object-cover" />
        <div>
          <h4 className="font-semibold">{author}</h4>
          <p className="text-sm text-gray-500">{role}</p>
        </div>
      </div>
    </div>
  )
}
