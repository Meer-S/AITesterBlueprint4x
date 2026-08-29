import { useEffect, useMemo, useRef, useState } from 'react'
import {
  DndContext,
  DragOverlay,
  KeyboardSensor,
  PointerSensor,
  closestCorners,
  useDroppable,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import {
  ArchiveRestore,
  BriefcaseBusiness,
  CalendarDays,
  Check,
  ChevronDown,
  Download,
  ExternalLink,
  FileText,
  GripVertical,
  Link2,
  Moon,
  MoreHorizontal,
  Pencil,
  Plus,
  Search,
  Sun,
  Trash2,
  Upload,
  X,
} from 'lucide-react'
import { getAllJobs, removeJob, replaceAllJobs, saveJob } from './db.js'

const STATUSES = [
  { id: 'wishlist', label: 'Wishlist', description: 'Saved for later', accent: 'border-l-slate-400', dot: 'bg-slate-400' },
  { id: 'applied', label: 'Applied', description: 'Application sent', accent: 'border-l-blue-500', dot: 'bg-blue-500' },
  { id: 'follow-up', label: 'Follow-up', description: 'Recruiter contacted', accent: 'border-l-amber-500', dot: 'bg-amber-500' },
  { id: 'interview', label: 'Interview', description: 'In active rounds', accent: 'border-l-violet-500', dot: 'bg-violet-500' },
  { id: 'offer', label: 'Offer', description: 'Offer received', accent: 'border-l-emerald-500', dot: 'bg-emerald-500' },
  { id: 'rejected', label: 'Rejected', description: 'Application closed', accent: 'border-l-rose-500', dot: 'bg-rose-500' },
]

const STATUS_IDS = new Set(STATUSES.map((status) => status.id))
const today = () => new Date().toISOString().slice(0, 10)

const emptyForm = () => ({
  company: '',
  role: '',
  linkedInUrl: '',
  resumeUsed: '',
  dateApplied: today(),
  salaryRange: '',
  notes: '',
  status: 'wishlist',
})

function createId() {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function formatRelativeDate(dateValue) {
  if (!dateValue) return 'Date not set'
  const applied = new Date(`${dateValue}T00:00:00`)
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  const days = Math.max(0, Math.floor((now - applied) / 86400000))
  if (days === 0) return 'Today'
  if (days === 1) return '1 day ago'
  return `${days} days ago`
}

function normalizeUrl(value) {
  const trimmed = value.trim()
  if (!trimmed) return ''
  return /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`
}

function JobCard({ job, accent, onEdit, onDelete, overlay = false }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const sortable = useSortable({ id: job.id, disabled: overlay })
  const style = overlay
    ? undefined
    : {
        transform: CSS.Transform.toString(sortable.transform),
        transition: sortable.transition,
        opacity: sortable.isDragging ? 0.35 : 1,
      }

  return (
    <article
      ref={sortable.setNodeRef}
      style={style}
      className={`group relative rounded-xl border border-slate-200 border-l-4 ${accent} bg-white p-4 shadow-card transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-700 dark:bg-slate-900 ${overlay ? 'w-[280px] rotate-2 shadow-modal' : ''}`}
    >
      <div className="flex items-start gap-2">
        <button
          type="button"
          className="mt-0.5 cursor-grab rounded-md p-1 text-slate-300 transition hover:bg-slate-100 hover:text-slate-500 active:cursor-grabbing dark:hover:bg-slate-800"
          aria-label={`Drag ${job.company} application`}
          {...sortable.attributes}
          {...sortable.listeners}
        >
          <GripVertical size={16} />
        </button>
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-sm font-semibold text-slate-950 dark:text-white">{job.company}</h3>
          <p className="mt-1 line-clamp-2 text-sm leading-5 text-slate-600 dark:text-slate-300">{job.role}</p>
        </div>
        {!overlay && (
          <div className="relative">
            <button
              type="button"
              className="rounded-md p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-white"
              aria-label={`Actions for ${job.company}`}
              aria-expanded={menuOpen}
              onClick={() => setMenuOpen((open) => !open)}
            >
              <MoreHorizontal size={18} />
            </button>
            {menuOpen && (
              <div className="absolute right-0 z-20 mt-1 w-32 overflow-hidden rounded-lg border border-slate-200 bg-white p-1 shadow-lg dark:border-slate-700 dark:bg-slate-800">
                <button
                  type="button"
                  className="menu-item"
                  onClick={() => {
                    setMenuOpen(false)
                    onEdit(job)
                  }}
                >
                  <Pencil size={14} /> Edit
                </button>
                <button
                  type="button"
                  className="menu-item text-rose-600 dark:text-rose-400"
                  onClick={() => {
                    setMenuOpen(false)
                    onDelete(job)
                  }}
                >
                  <Trash2 size={14} /> Delete
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        {job.resumeUsed && (
          <span className="inline-flex max-w-full items-center gap-1 truncate rounded-md bg-indigo-50 px-2 py-1 text-[11px] font-medium text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300">
            <FileText size={12} />
            <span className="truncate">{job.resumeUsed}</span>
          </span>
        )}
        {job.salaryRange && (
          <span className="rounded-md bg-slate-100 px-2 py-1 text-[11px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            {job.salaryRange}
          </span>
        )}
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400">
        <span className="inline-flex items-center gap-1.5">
          <CalendarDays size={13} /> {formatRelativeDate(job.dateApplied)}
        </span>
        {job.linkedInUrl && (
          <a
            href={job.linkedInUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 font-medium text-blue-600 hover:text-blue-700 hover:underline dark:text-blue-400"
            onPointerDown={(event) => event.stopPropagation()}
          >
            LinkedIn <ExternalLink size={12} />
          </a>
        )}
      </div>
    </article>
  )
}

function KanbanColumn({ status, jobs, onEdit, onDelete }) {
  const { setNodeRef, isOver } = useDroppable({ id: `column-${status.id}` })

  return (
    <section className="flex min-h-0 w-[300px] shrink-0 flex-col rounded-2xl bg-slate-100/70 p-3 dark:bg-slate-900/70">
      <header className="mb-3 flex items-center justify-between px-1">
        <div>
          <div className="flex items-center gap-2">
            <span className={`h-2.5 w-2.5 rounded-full ${status.dot}`} />
            <h2 className="text-sm font-semibold text-slate-900 dark:text-white">{status.label}</h2>
            <span className="rounded-full bg-white px-2 py-0.5 text-xs font-semibold text-slate-500 shadow-sm dark:bg-slate-800 dark:text-slate-300">
              {jobs.length}
            </span>
          </div>
          <p className="mt-1 pl-[18px] text-[11px] text-slate-500 dark:text-slate-500">{status.description}</p>
        </div>
      </header>

      <div
        ref={setNodeRef}
        className={`column-scroll min-h-[180px] flex-1 space-y-3 overflow-y-auto rounded-xl p-1 transition ${isOver ? 'bg-blue-50 ring-2 ring-inset ring-blue-300 dark:bg-blue-950/20 dark:ring-blue-700' : ''}`}
      >
        <SortableContext items={jobs.map((job) => job.id)} strategy={verticalListSortingStrategy}>
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} accent={status.accent} onEdit={onEdit} onDelete={onDelete} />
          ))}
        </SortableContext>
        {jobs.length === 0 && (
          <div className="grid min-h-32 place-items-center rounded-xl border border-dashed border-slate-300 px-4 text-center text-xs text-slate-400 dark:border-slate-700 dark:text-slate-500">
            Drop a job here
          </div>
        )}
      </div>
    </section>
  )
}

function JobModal({ job, resumeNames, onClose, onSave }) {
  const [form, setForm] = useState(job ? { ...job } : emptyForm())
  const [errors, setErrors] = useState({})
  const firstInput = useRef(null)

  useEffect(() => {
    firstInput.current?.focus()
    const onKeyDown = (event) => {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [onClose])

  const update = (field) => (event) => {
    setForm((current) => ({ ...current, [field]: event.target.value }))
    setErrors((current) => ({ ...current, [field]: '' }))
  }

  const submit = (event) => {
    event.preventDefault()
    const nextErrors = {}
    if (!form.company.trim()) nextErrors.company = 'Company name is required.'
    if (!form.role.trim()) nextErrors.role = 'Job title is required.'
    if (!form.dateApplied) nextErrors.dateApplied = 'Choose a date.'
    if (form.linkedInUrl.trim()) {
      try {
        const parsed = new URL(normalizeUrl(form.linkedInUrl))
        if (!['http:', 'https:'].includes(parsed.protocol)) throw new Error('Invalid protocol')
      } catch {
        nextErrors.linkedInUrl = 'Enter a valid web address.'
      }
    }
    if (Object.keys(nextErrors).length) {
      setErrors(nextErrors)
      return
    }

    onSave({
      ...form,
      id: form.id ?? createId(),
      company: form.company.trim(),
      role: form.role.trim(),
      linkedInUrl: normalizeUrl(form.linkedInUrl),
      resumeUsed: form.resumeUsed.trim(),
      salaryRange: form.salaryRange.trim(),
      notes: form.notes.trim(),
      updatedAt: new Date().toISOString(),
      createdAt: form.createdAt ?? new Date().toISOString(),
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-slate-950/55 p-0 backdrop-blur-sm sm:items-center sm:p-6" onMouseDown={onClose}>
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="job-modal-title"
        className="max-h-[94vh] w-full overflow-y-auto rounded-t-2xl bg-white shadow-modal dark:bg-slate-900 sm:max-w-2xl sm:rounded-2xl"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white/95 px-6 py-5 backdrop-blur dark:border-slate-800 dark:bg-slate-900/95">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600 dark:text-blue-400">Job details</p>
            <h2 id="job-modal-title" className="mt-1 text-xl font-semibold text-slate-950 dark:text-white">
              {job ? 'Edit application' : 'Add a new opportunity'}
            </h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose} aria-label="Close dialog">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={submit} className="space-y-5 p-6">
          <div className="grid gap-5 sm:grid-cols-2">
            <Field label="Company name" required error={errors.company}>
              <input ref={firstInput} className="input" value={form.company} onChange={update('company')} placeholder="e.g. Atlassian" />
            </Field>
            <Field label="Job title / role" required error={errors.role}>
              <input className="input" value={form.role} onChange={update('role')} placeholder="e.g. Lead SDET" />
            </Field>
          </div>

          <Field label="LinkedIn job URL" error={errors.linkedInUrl}>
            <div className="relative">
              <Link2 className="input-icon" size={17} />
              <input className="input pl-10" value={form.linkedInUrl} onChange={update('linkedInUrl')} placeholder="linkedin.com/jobs/view/..." inputMode="url" />
            </div>
          </Field>

          <div className="grid gap-5 sm:grid-cols-2">
            <Field label="Resume used">
              <input className="input" list="resume-options" value={form.resumeUsed} onChange={update('resumeUsed')} placeholder="QA_Lead_Resume" />
              <datalist id="resume-options">
                {resumeNames.map((name) => <option key={name} value={name} />)}
              </datalist>
            </Field>
            <Field label="Salary range">
              <input className="input" value={form.salaryRange} onChange={update('salaryRange')} placeholder="₹25–30 LPA" />
            </Field>
          </div>

          <div className="grid gap-5 sm:grid-cols-2">
            <Field label="Date applied" required error={errors.dateApplied}>
              <input type="date" className="input" value={form.dateApplied} onChange={update('dateApplied')} />
            </Field>
            <Field label="Status">
              <div className="relative">
                <select className="input appearance-none pr-10" value={form.status} onChange={update('status')}>
                  {STATUSES.map((status) => <option key={status.id} value={status.id}>{status.label}</option>)}
                </select>
                <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              </div>
            </Field>
          </div>

          <Field label="Notes">
            <textarea className="input min-h-28 resize-y py-3" value={form.notes} onChange={update('notes')} placeholder="Recruiter, referral, next steps, interview notes..." />
          </Field>

          <div className="flex flex-col-reverse gap-3 border-t border-slate-200 pt-5 dark:border-slate-800 sm:flex-row sm:justify-end">
            <button type="button" className="button-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="button-primary">
              <Check size={17} /> {job ? 'Save changes' : 'Add to tracker'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function Field({ label, required = false, error, children }) {
  return (
    <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">
      <span>{label}{required && <span className="ml-1 text-rose-500">*</span>}</span>
      <div className="mt-2">{children}</div>
      {error && <span className="mt-1.5 block text-xs font-medium text-rose-600 dark:text-rose-400">{error}</span>}
    </label>
  )
}

function ConfirmDelete({ job, onCancel, onConfirm }) {
  return (
    <div className="fixed inset-0 z-[60] grid place-items-center bg-slate-950/55 p-5 backdrop-blur-sm" onMouseDown={onCancel}>
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-modal dark:bg-slate-900" onMouseDown={(event) => event.stopPropagation()}>
        <div className="grid h-11 w-11 place-items-center rounded-xl bg-rose-50 text-rose-600 dark:bg-rose-950/50 dark:text-rose-400">
          <Trash2 size={20} />
        </div>
        <h2 className="mt-5 text-lg font-semibold text-slate-950 dark:text-white">Delete this application?</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
          <strong>{job.company}</strong> — {job.role} will be permanently removed from this browser.
        </p>
        <div className="mt-6 flex justify-end gap-3">
          <button type="button" className="button-secondary" onClick={onCancel}>Keep it</button>
          <button type="button" className="button-danger" onClick={onConfirm}>Delete job</button>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [sortOrder, setSortOrder] = useState('newest')
  const [modalJob, setModalJob] = useState(undefined)
  const [modalOpen, setModalOpen] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const [activeJob, setActiveJob] = useState(null)
  const [toast, setToast] = useState('')
  const [theme, setTheme] = useState(() => localStorage.getItem('job-tracker-theme') ?? 'light')
  const importInput = useRef(null)

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  useEffect(() => {
    let mounted = true
    getAllJobs()
      .then((records) => {
        if (mounted) setJobs(records)
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })
    return () => { mounted = false }
  }, [])

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    localStorage.setItem('job-tracker-theme', theme)
  }, [theme])

  useEffect(() => {
    if (!toast) return undefined
    const timer = window.setTimeout(() => setToast(''), 2600)
    return () => window.clearTimeout(timer)
  }, [toast])

  const resumeNames = useMemo(
    () => [...new Set(jobs.map((job) => job.resumeUsed).filter(Boolean))].sort((a, b) => a.localeCompare(b)),
    [jobs],
  )

  const visibleJobs = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase()
    return jobs
      .filter((job) => !normalizedQuery || `${job.company} ${job.role}`.toLowerCase().includes(normalizedQuery))
      .sort((a, b) => {
        const comparison = new Date(b.dateApplied) - new Date(a.dateApplied)
        return sortOrder === 'newest' ? comparison : -comparison
      })
  }, [jobs, query, sortOrder])

  const jobsByStatus = useMemo(
    () => Object.fromEntries(STATUSES.map((status) => [status.id, visibleJobs.filter((job) => job.status === status.id)])),
    [visibleJobs],
  )

  const showToast = (message) => setToast(message)

  const openNew = () => {
    setModalJob(undefined)
    setModalOpen(true)
  }

  const openEdit = (job) => {
    setModalJob(job)
    setModalOpen(true)
  }

  const handleSave = async (job) => {
    await saveJob(job)
    setJobs((current) => {
      const exists = current.some((item) => item.id === job.id)
      return exists ? current.map((item) => item.id === job.id ? job : item) : [...current, job]
    })
    setModalOpen(false)
    showToast(modalJob ? 'Application updated' : 'Application added')
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    await removeJob(deleteTarget.id)
    setJobs((current) => current.filter((job) => job.id !== deleteTarget.id))
    setDeleteTarget(null)
    showToast('Application deleted')
  }

  const handleDragStart = ({ active }) => {
    setActiveJob(jobs.find((job) => job.id === active.id) ?? null)
  }

  const handleDragEnd = async ({ active, over }) => {
    setActiveJob(null)
    if (!over) return
    const job = jobs.find((item) => item.id === active.id)
    if (!job) return
    const targetStatus = String(over.id).startsWith('column-')
      ? String(over.id).replace('column-', '')
      : jobs.find((item) => item.id === over.id)?.status
    if (!targetStatus || targetStatus === job.status || !STATUS_IDS.has(targetStatus)) return
    const updated = { ...job, status: targetStatus, updatedAt: new Date().toISOString() }
    setJobs((current) => current.map((item) => item.id === job.id ? updated : item))
    await saveJob(updated)
    showToast(`Moved to ${STATUSES.find((status) => status.id === targetStatus)?.label}`)
  }

  const exportData = () => {
    const payload = JSON.stringify({ version: 1, exportedAt: new Date().toISOString(), jobs }, null, 2)
    const url = URL.createObjectURL(new Blob([payload], { type: 'application/json' }))
    const link = document.createElement('a')
    link.href = url
    link.download = `job-tracker-backup-${today()}.json`
    link.click()
    URL.revokeObjectURL(url)
    showToast('Backup exported')
  }

  const importData = async (event) => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    try {
      const parsed = JSON.parse(await file.text())
      const incoming = Array.isArray(parsed) ? parsed : parsed.jobs
      if (!Array.isArray(incoming)) throw new Error('Backup does not contain a jobs array.')
      const normalized = incoming.map((job) => {
        if (!job.company?.trim() || !job.role?.trim()) throw new Error('Every imported job needs a company and role.')
        return {
          ...emptyForm(),
          ...job,
          id: job.id || createId(),
          company: job.company.trim(),
          role: job.role.trim(),
          status: STATUS_IDS.has(job.status) ? job.status : 'wishlist',
          dateApplied: job.dateApplied || today(),
          linkedInUrl: job.linkedInUrl ? normalizeUrl(job.linkedInUrl) : '',
        }
      })
      if (jobs.length && !window.confirm(`Replace ${jobs.length} existing job${jobs.length === 1 ? '' : 's'} with ${normalized.length} imported job${normalized.length === 1 ? '' : 's'}?`)) return
      await replaceAllJobs(normalized)
      setJobs(normalized)
      showToast(`${normalized.length} job${normalized.length === 1 ? '' : 's'} restored`)
    } catch (error) {
      window.alert(`Could not import this backup. ${error.message}`)
    }
  }

  const activeStatus = activeJob ? STATUSES.find((status) => status.id === activeJob.status) : null

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 transition-colors dark:bg-slate-950 dark:text-white">
      <header className="border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
        <div className="mx-auto flex max-w-[1920px] items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex min-w-0 items-center gap-3">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-slate-950 text-white shadow-sm dark:bg-white dark:text-slate-950">
              <BriefcaseBusiness size={20} />
            </div>
            <div className="min-w-0">
              <h1 className="truncate text-lg font-semibold tracking-tight text-slate-950 dark:text-white">Job Tracker AI</h1>
              <p className="truncate text-xs text-slate-500 dark:text-slate-400">Private by default · Stored only in this browser</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button type="button" className="icon-button" onClick={() => setTheme((current) => current === 'dark' ? 'light' : 'dark')} aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button type="button" className="button-primary" onClick={openNew}>
              <Plus size={18} /> <span className="hidden sm:inline">Add job</span><span className="sm:hidden">Add</span>
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1920px] px-4 py-5 sm:px-6 lg:px-8">
        <div className="mb-5 flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div className="grid grid-cols-3 divide-x divide-slate-200 rounded-xl border border-slate-200 bg-white px-2 py-3 shadow-sm dark:divide-slate-700 dark:border-slate-800 dark:bg-slate-900 sm:w-fit sm:min-w-[430px]">
            <Metric label="Total jobs" value={jobs.length} />
            <Metric label="Interviews" value={jobs.filter((job) => job.status === 'interview').length} />
            <Metric label="Offers" value={jobs.filter((job) => job.status === 'offer').length} />
          </div>

          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <div className="relative min-w-0 sm:w-72">
              <Search className="input-icon" size={17} />
              <input className="input pl-10" type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search company or role..." aria-label="Search jobs" />
            </div>
            <div className="relative sm:w-40">
              <select className="input appearance-none pr-9 text-sm" value={sortOrder} onChange={(event) => setSortOrder(event.target.value)} aria-label="Sort jobs">
                <option value="newest">Newest first</option>
                <option value="oldest">Oldest first</option>
              </select>
              <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
            </div>
            <button type="button" className="button-secondary" onClick={exportData} disabled={!jobs.length} title="Export JSON backup">
              <Download size={16} /> <span className="hidden sm:inline">Export</span>
            </button>
            <button type="button" className="button-secondary" onClick={() => importInput.current?.click()} title="Import JSON backup">
              <Upload size={16} /> <span className="hidden sm:inline">Import</span>
            </button>
            <input ref={importInput} type="file" accept="application/json,.json" className="hidden" onChange={importData} />
          </div>
        </div>

        {loading ? (
          <div className="grid min-h-[420px] place-items-center rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
            <div className="text-center">
              <ArchiveRestore className="mx-auto animate-pulse text-blue-500" size={28} />
              <p className="mt-3 text-sm text-slate-500">Loading your local tracker...</p>
            </div>
          </div>
        ) : (
          <DndContext sensors={sensors} collisionDetection={closestCorners} onDragStart={handleDragStart} onDragEnd={handleDragEnd} onDragCancel={() => setActiveJob(null)}>
            <div className="board-scroll flex h-[calc(100vh-215px)] min-h-[480px] gap-4 overflow-x-auto pb-3">
              {STATUSES.map((status) => (
                <KanbanColumn key={status.id} status={status} jobs={jobsByStatus[status.id]} onEdit={openEdit} onDelete={setDeleteTarget} />
              ))}
            </div>
            <DragOverlay dropAnimation={{ duration: 180, easing: 'ease-out' }}>
              {activeJob && activeStatus ? <JobCard job={activeJob} accent={activeStatus.accent} overlay /> : null}
            </DragOverlay>
          </DndContext>
        )}
      </main>

      {modalOpen && <JobModal job={modalJob} resumeNames={resumeNames} onClose={() => setModalOpen(false)} onSave={handleSave} />}
      {deleteTarget && <ConfirmDelete job={deleteTarget} onCancel={() => setDeleteTarget(null)} onConfirm={handleDelete} />}

      {toast && (
        <div role="status" className="fixed bottom-5 left-1/2 z-[70] flex -translate-x-1/2 items-center gap-2 rounded-full bg-slate-950 px-4 py-2.5 text-sm font-medium text-white shadow-modal dark:bg-white dark:text-slate-950">
          <Check size={16} className="text-emerald-400 dark:text-emerald-600" /> {toast}
        </div>
      )}
    </div>
  )
}

function Metric({ label, value }) {
  return (
    <div className="px-4">
      <p className="text-lg font-semibold tabular-nums text-slate-950 dark:text-white">{value}</p>
      <p className="mt-0.5 text-[11px] font-medium text-slate-500 dark:text-slate-400">{label}</p>
    </div>
  )
}
