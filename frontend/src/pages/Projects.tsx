import { useState, useEffect } from 'react'
import { listProjects, getProjectGenerations } from '../api'
import { useAuth } from '../context/AuthContext'
import { Project } from '../types'
import { Link } from 'react-router-dom'
import { Lock, Home, Plus, Armchair, X, Download, Maximize2 } from 'lucide-react'
import { GenerationDone } from '../types'

interface ProjectWithThumbnail extends Project {
  thumbnail_url?: string
  latest_generation?: GenerationDone
}

function ImageModal({ image_url, onClose }: { image_url: string; onClose: () => void }) {
  const downloadImage = async () => {
    try {
      const response = await fetch(image_url)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `roomstyle-design-${Date.now()}.png`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Download failed:', err)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-rs-border">
          <h3 className="text-lg font-semibold text-rs-dark">Generated Design</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-stone-100 rounded-full transition-colors"
          >
            <X size={24} className="text-stone-600" />
          </button>
        </div>

        {/* Image */}
        <div className="flex-1 flex items-center justify-center p-6 bg-stone-50 overflow-auto">
          <img
            src={image_url}
            alt="Generated design"
            className="max-w-full max-h-[70vh] rounded-2xl shadow-lg object-contain"
          />
        </div>

        {/* Footer */}
        <div className="flex items-center gap-3 p-6 border-t border-rs-border justify-end">
          <button
            onClick={onClose}
            className="btn-secondary"
          >
            Close
          </button>
          <button
            onClick={downloadImage}
            className="btn-primary flex items-center gap-2"
          >
            <Download size={18} />
            Download
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Projects() {
  const { token } = useAuth()
  const [projects, setProjects] = useState<ProjectWithThumbnail[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedImage, setSelectedImage] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    setLoading(true)
    
    listProjects(token)
      .then(async (projectList) => {
        // Fetch latest generation for each project to get thumbnail
        const projectsWithThumbnails = await Promise.all(
          projectList.map(async (project) => {
            try {
              if (project.generation_ids.length > 0) {
                const generations = await getProjectGenerations(token, project.project_id)
                if (generations.length > 0) {
                  // Get the most recent generation
                  const latest = generations[generations.length - 1]
                  return {
                    ...project,
                    thumbnail_url: latest.image_url,
                    latest_generation: latest,
                  }
                }
              }
            } catch (err) {
              console.error(`Failed to fetch generations for project ${project.project_id}:`, err)
            }
            return project
          })
        )
        setProjects(projectsWithThumbnails)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [token])

  if (!token) {
    return (
      <main className="max-w-2xl mx-auto px-4 py-20 text-center">
        <Lock size={48} className="mx-auto mb-3 text-stone-300" />
        <p className="text-stone-500">Sign in to view your projects.</p>
      </main>
    )
  }

  return (
    <main className="max-w-6xl mx-auto px-4 py-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-rs-dark mb-1">My Projects</h1>
          <p className="text-sm text-stone-500">View and manage all your room designs</p>
        </div>
        <Link to="/" className="btn-primary flex items-center gap-2">
          <Plus size={18} />
          New Design
        </Link>
      </div>

      {loading && (
        <div className="text-center py-20 text-stone-400">
          <div className="inline-flex items-center gap-2">
            <div className="w-2 h-2 bg-stone-400 rounded-full animate-bounce" />
            <div className="w-2 h-2 bg-stone-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-stone-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <p className="mt-3">Loading your projects…</p>
        </div>
      )}
      {error && <p className="text-red-500 text-sm bg-red-50 p-4 rounded-xl">{error}</p>}

      {!loading && projects.length === 0 && (
        <div className="text-center py-20 text-stone-400">
          <Home size={48} className="mx-auto mb-3 text-stone-300" />
          <p className="mb-4 font-medium">No projects yet</p>
          <p className="text-sm mb-6">Start creating your first room design to see it here</p>
          <Link to="/" className="btn-primary inline-flex items-center gap-2">
            <Plus size={18} />
            Create Design
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((p) => (
          <div key={p.project_id} className="card overflow-hidden hover:shadow-premium-hover transition-all duration-300 group">
            {/* Thumbnail */}
            <div className="relative w-full h-40 bg-gradient-to-br from-cream to-stone-100 overflow-hidden">
              {p.thumbnail_url && p.latest_generation ? (
                <>
                  <img
                    src={p.thumbnail_url}
                    alt={p.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <button
                    onClick={() => setSelectedImage(p.thumbnail_url!)}
                    className="absolute inset-0 flex items-center justify-center bg-black/0 group-hover:bg-black/40 transition-colors duration-300 opacity-0 group-hover:opacity-100"
                  >
                    <div className="flex items-center gap-2 bg-white/90 px-4 py-2 rounded-full font-medium text-sm text-rs-dark">
                      <Maximize2 size={16} />
                      View
                    </div>
                  </button>
                </>
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Armchair size={56} className="text-stone-300" />
                </div>
              )}
            </div>

            {/* Content */}
            <div className="p-4">
              <h3 className="font-semibold text-sm text-rs-dark truncate mb-2">{p.name}</h3>
              <p className="text-xs text-stone-400 mb-3">
                {new Date(p.created_at).toLocaleDateString('en-SG', {
                  day: 'numeric', month: 'short', year: 'numeric',
                })}
              </p>

              {/* Stats */}
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-stone-100 text-stone-600 text-xs rounded-full font-medium">
                  {p.photo_ids.length} photo{p.photo_ids.length !== 1 ? 's' : ''}
                </span>
                <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-stone-100 text-stone-600 text-xs rounded-full font-medium">
                  {p.generation_ids.length} design{p.generation_ids.length !== 1 ? 's' : ''}
                </span>
                {p.budget_limit && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-50 text-amber-700 text-xs rounded-full font-medium">
                    S${p.budget_limit}
                  </span>
                )}
              </div>

              {/* Action */}
              {p.thumbnail_url && p.latest_generation && (
                <button
                  onClick={() => setSelectedImage(p.thumbnail_url!)}
                  className="w-full btn-secondary text-xs"
                >
                  View Latest Design
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <ImageModal
          image_url={selectedImage}
          onClose={() => setSelectedImage(null)}
        />
      )}
    </main>
  )
}
