import { openDB } from 'idb'

const DB_NAME = 'job-tracker-ai'
const STORE_NAME = 'jobs'

const dbPromise = openDB(DB_NAME, 1, {
  upgrade(db) {
    const jobs = db.createObjectStore(STORE_NAME, { keyPath: 'id' })
    jobs.createIndex('status', 'status')
    jobs.createIndex('dateApplied', 'dateApplied')
  },
})

export async function getAllJobs() {
  return (await dbPromise).getAll(STORE_NAME)
}

export async function saveJob(job) {
  return (await dbPromise).put(STORE_NAME, job)
}

export async function removeJob(id) {
  return (await dbPromise).delete(STORE_NAME, id)
}

export async function replaceAllJobs(jobs) {
  const db = await dbPromise
  const tx = db.transaction(STORE_NAME, 'readwrite')
  await tx.store.clear()
  await Promise.all(jobs.map((job) => tx.store.put(job)))
  await tx.done
}
