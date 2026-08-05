import { useState, useRef, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router'
import Header from '../components/Header'
import TitrePage from '../components/TitrePage'
import UploadIcon from '../assets/cloud-upload.svg?react'
import { lancerAnalyse } from '../services/api'
import type { Analyse } from '../types'
import './pages.css'
import './Analysis.css'

type Exposition = 'Soleil' | 'Mi-ombre' | 'Ombre'
type TypeCulture = 'En pot' | 'Pleine terre'
type Lieu = 'Intérieur' | 'Extérieur'

interface AnalysisProps {
  onResultat: (analyse: Analyse) => void
}

function Analysis({ onResultat }: AnalysisProps) {
  const [fichier, setFichier] = useState<File | null>(null)
  const [apercu, setApercu] = useState<string | null>(null)
  const [survol, setSurvol] = useState(false)
  const [typePlante, setTypePlante] = useState('')
  const [exposition, setExposition] = useState<Exposition>('Soleil')
  const [lieu, setLieu] = useState<Lieu>('Intérieur')
  const [typeCulture, setTypeCulture] = useState<TypeCulture>('En pot')
  const [chargement, setChargement] = useState(false)
  const [erreur, setErreur] = useState('')
  const [webcamActive, setWebcamActive] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const streamRef = useRef<MediaStream>(null)
  const pendingStremRef = useRef<MediaStream | null>(null)
  const navigate = useNavigate()

  // Fonction pour ouvrir la caméra
  const ouvrirWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {facingMode: 'environment'}, // Utilisation de la caméra arrière sur mobile
        audio: false, // On souhaite prendre une photo, pas une video donc inutile d'activer le micro
      })
      streamRef.current = stream
      pendingStremRef.current = stream
      setWebcamActive(true)
    } catch {
      setErreur("Impossible d'accéder à la caméra")
    }
  }

  useEffect(() => {
    if (webcamActive && videoRef.current && pendingStremRef.current) {
      videoRef.current.srcObject = pendingStremRef.current
      pendingStremRef.current = null
    }
  }, [webcamActive]) // déclenchment quand l'état de la webcam change, i.e. webcamActive change

  // Fonction pour fermer la caméra proprement (i.e. libère la ressource)
  const fermerWebcam = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop())
    streamRef.current = null
    setWebcamActive(false)
  }, [])

  // Capturer une photo depuis le flux vidéo pour l'analyse
  const capturerPhoto = () => {
    const video =videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d')?.drawImage(video,0,0)

    canvas.toBlob((blob) => {
      if (!blob) return
      const file = new File([blob], 'photo.jpg', {type: 'image/jpeg'})
      traiterFichier(file) // on utilise la fonction de taitement et contrôle de l'image fournie par l'utilisateur
      fermerWebcam() // on ferme proprement la ressource
    }, 'image/jpeg', 0.92)
  }

  const traiterFichier = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setErreur('Format non supporté. Utilisez JPG ou PNG.')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setErreur('La photo dépasse 10 Mo.')
      return
    }
    setErreur('')
    setFichier(file)
    setApercu(URL.createObjectURL(file))
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setSurvol(false)
    const file = e.dataTransfer.files[0]
    if (file) traiterFichier(file)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) traiterFichier(file)
  }

  const handleSubmit = async () => {
    if (!fichier) {
      setErreur('Veuillez sélectionner une photo.')
      return
    }
    setErreur('')
    setChargement(true)
    try {
      const resultat = await lancerAnalyse({
        image: fichier,
        typePlante: typePlante || undefined,
        exposition,
        lieu,
        typeCulture,
      })
      onResultat(resultat)
      navigate('/resultat')
    } catch {
      setErreur("Une erreur est survenue lors de l'analyse.")
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="page">
      <TitrePage titre='Analyse' />
      <Header />

      <main className="page__main">
        <div className="analysis-layout">

          {/* Colonne gauche : zone de dépôt */}
          <section className="analysis-upload">
            <h1 className="page__titre">Analyse</h1>

            <div
              className={[
                'dropzone',
                survol ? 'dropzone--survol' : '',
                apercu ? 'dropzone--avec-apercu' : '',
              ].join(' ')}
              onDragOver={(e) => { e.preventDefault(); setSurvol(true) }}
              onDragLeave={() => setSurvol(false)}
              onDrop={handleDrop}
              onClick={() => !apercu && inputRef.current?.click()}
            >
              {apercu ? (
                <img src={apercu} alt="Aperçu" className="dropzone__apercu" />
              ) : (
                <>
                  <UploadIcon className="dropzone__icone" />
                  <p className="dropzone__texte">Glisser-déposer une photo</p>
                  <p className="dropzone__sous-texte">JPG, PNG — 10 Mo max</p>
                </>
              )}
            </div>

            <input
              ref={inputRef}
              type="file"
              accept="image/jpeg,image/png"
              className="analysis-upload__input-hidden"
              onChange={handleFileChange}
            />

            <div className="analysis-upload__boutons">
              <button className="btn btn--primary" onClick={() => inputRef.current?.click()}>
                Choisir un fichier
              </button>
              <button className="btn btn--outline" onClick={ouvrirWebcam}>
                Prendre une photo
              </button>
            </div>

            {/* Bloc webcam — visible uniquement quand la caméra est active */}
            {webcamActive && (
              <div className="webcam-bloc">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline       // obligatoire sur iOS pour éviter le mode plein écran
                  className="webcam-video"
                />
                <canvas ref={canvasRef} className="webcam-canvas-hidden" />
                <div className="webcam-actions">
                  <button className="btn btn--primary" onClick={capturerPhoto}>
                    📸 Capturer
                  </button>
                  <button className="btn btn--outline" onClick={fermerWebcam}>
                    Annuler
                  </button>
                </div>
              </div>
            )}

            {apercu && (
              <button
                className="analysis-upload__changer"
                onClick={() => { setFichier(null); setApercu(null) }}
              >
                Changer la photo
              </button>
            )}
          </section>

          {/* Colonne droite : contexte optionnel */}
          <section className="analysis-context">
            <h2 className="analysis-context__titre">Contexte optionnel</h2>

            <div className="form-group">
              <label htmlFor="typeplante" className="form-group__label">Type de plante</label>
              <input
                id="typeplante"
                type="text"
                className="form-group__input"
                placeholder="Ex : Monstera, Ficus, Rose ..."
                value={typePlante}
                onChange={(e) => setTypePlante(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-group__label">Exposition</label>
              <div className="toggle-group">
                {(['Soleil', 'Mi-ombre', 'Ombre'] as Exposition[]).map((opt) => (
                  <button
                    key={opt}
                    className={exposition === opt ? 'toggle-btn toggle-btn--active' : 'toggle-btn'}
                    onClick={() => setExposition(opt)}
                  >
                    {opt === 'Soleil' && '☀ '}
                    {opt === 'Mi-ombre' && '◑ '}
                    {opt === 'Ombre' && '☾ '}
                    {opt}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="lieu" className="form-group__label">Lieu</label>
              <div className="select-wrap">
                <select
                  id="lieu"
                  className="form-group__select"
                  value={lieu}
                  onChange={(e) => setLieu(e.target.value as Lieu)}
                >
                  <option value="Intérieur">Intérieur</option>
                  <option value="Extérieur">Extérieur</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-group__label">Type de culture</label>
              <div className="toggle-group">
                {(['En pot', 'Pleine terre'] as TypeCulture[]).map((opt) => (
                  <button
                    key={opt}
                    className={typeCulture === opt ? 'toggle-btn toggle-btn--active' : 'toggle-btn'}
                    onClick={() => setTypeCulture(opt)}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>

            {erreur && <p className="msg-erreur">{erreur}</p>}

            <button
              className="btn btn--primary btn--full analysis-context__submit"
              onClick={handleSubmit}
              disabled={chargement}
            >
              {chargement ? 'Analyse en cours…' : "Lancer l'analyse"}
            </button>
          </section>

        </div>
      </main>
    </div>
  )
}

export default Analysis
