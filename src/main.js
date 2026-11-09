import * as pdfjsLib from 'pdfjs-dist';
import pdfWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.js?url';
import { PDFDocument } from 'pdf-lib';

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerUrl;

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const copyPathBtn = document.getElementById('copyPathBtn');
const targetPathText = document.getElementById('targetPathText');

const presetsGrid = document.getElementById('presetsGrid');
const dpiInput = document.getElementById('dpiInput');
const dpiValue = document.getElementById('dpiValue');
const qualityInput = document.getElementById('qualityInput');
const qualityValue = document.getElementById('qualityValue');
const contrastBoostInput = document.getElementById('contrastBoostInput');
const grayscaleInput = document.getElementById('grayscaleInput');

const recompressBtn = document.getElementById('recompressBtn');
const downloadBtn = document.getElementById('downloadBtn');

const origSizeVal = document.getElementById('origSizeVal');
const newSizeVal = document.getElementById('newSizeVal');
const savingsVal = document.getElementById('savingsVal');

const progressWrap = document.getElementById('progressWrap');
const progressText = document.getElementById('progressText');
const progressPercent = document.getElementById('progressPercent');
const progressBar = document.getElementById('progressBar');

const pageNav = document.getElementById('pageNav');
const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');
const pageIndicator = document.getElementById('pageIndicator');
const toggleZoomBtn = document.getElementById('toggleZoomBtn');
const previewSub = document.getElementById('previewSub');
const emptyPreview = document.getElementById('emptyPreview');
const previewCanvas = document.getElementById('previewCanvas');

let sourceFile = null;
let sourceBytes = null;
let loadedPdfDoc = null;
let compressedPdfBytes = null;
let renderedPagesDataUrls = [];
let currentPageIndex = 0;
let isActualZoom = false;
let isProcessing = false;

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const idx = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const val = bytes / Math.pow(1024, idx);
  return `${val.toFixed(idx === 0 ? 0 : 2)} ${units[idx]}`;
}

copyPathBtn.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(targetPathText.textContent.trim());
    const prev = copyPathBtn.textContent;
    copyPathBtn.textContent = 'Cale copiată în Clipboard!';
    setTimeout(() => {
      copyPathBtn.textContent = prev;
    }, 2000);
  } catch {
    // Fallback selection
    const range = document.createRange();
    range.selectNodeContents(targetPathText);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
  }
});

dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    fileInput.click();
  }
});

dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
    handleFileSelect(e.dataTransfer.files[0]);
  }
});

fileInput.addEventListener('change', (e) => {
  if (e.target.files && e.target.files.length > 0) {
    handleFileSelect(e.target.files[0]);
  }
});

presetsGrid.addEventListener('click', (e) => {
  const btn = e.target.closest('.preset-btn');
  if (!btn) return;
  document.querySelectorAll('.preset-btn').forEach((b) => b.classList.remove('active'));
  btn.classList.add('active');

  const dpi = Number(btn.dataset.dpi);
  const quality = Math.round(Number(btn.dataset.quality) * 100);

  dpiInput.value = String(dpi);
  dpiValue.textContent = `${dpi} DPI`;
  qualityInput.value = String(quality);
  qualityValue.textContent = `${quality}%`;

  if (loadedPdfDoc && !isProcessing) {
    compressLoadedPdf();
  }
});

dpiInput.addEventListener('input', () => {
  dpiValue.textContent = `${dpiInput.value} DPI`;
  clearActivePresets();
});

dpiInput.addEventListener('change', () => {
  if (loadedPdfDoc && !isProcessing) compressLoadedPdf();
});

qualityInput.addEventListener('input', () => {
  qualityValue.textContent = `${qualityInput.value}%`;
  clearActivePresets();
});

qualityInput.addEventListener('change', () => {
  if (loadedPdfDoc && !isProcessing) compressLoadedPdf();
});

contrastBoostInput.addEventListener('change', () => {
  if (loadedPdfDoc && !isProcessing) compressLoadedPdf();
});

grayscaleInput.addEventListener('change', () => {
  if (loadedPdfDoc && !isProcessing) compressLoadedPdf();
});

recompressBtn.addEventListener('click', () => {
  if (loadedPdfDoc && !isProcessing) compressLoadedPdf();
});

function clearActivePresets() {
  document.querySelectorAll('.preset-btn').forEach((b) => b.classList.remove('active'));
}

async function handleFileSelect(file) {
  if (!file) return;
  sourceFile = file;
  origSizeVal.textContent = formatBytes(file.size);
  newSizeVal.textContent = 'Se calculează...';
  savingsVal.textContent = '...';

  const arrayBuffer = await file.arrayBuffer();
  sourceBytes = new Uint8Array(arrayBuffer);

  const loadingTask = pdfjsLib.getDocument({ data: sourceBytes.slice() });
  loadedPdfDoc = await loadingTask.promise;
  currentPageIndex = 0;

  previewSub.textContent = `Fișier încărcat: ${file.name} (${loadedPdfDoc.numPages} pagini)`;
  recompressBtn.disabled = false;

  await compressLoadedPdf();
}

function applyReadabilityEnhancement(ctx, width, height, boostContrast, makeGrayscale) {
  if (!boostContrast && !makeGrayscale) return;
  const imgData = ctx.getImageData(0, 0, width, height);
  const data = imgData.data;

  // Mild S-curve / contrast stretch that keeps dark text crisp and cleans noisy scanner backgrounds
  const contrastFactor = boostContrast ? 1.18 : 1.0;

  for (let i = 0; i < data.length; i += 4) {
    let r = data[i];
    let g = data[i + 1];
    let b = data[i + 2];

    if (makeGrayscale) {
      const lum = 0.299 * r + 0.587 * g + 0.114 * b;
      r = lum;
      g = lum;
      b = lum;
    }

    if (boostContrast) {
      r = (r - 128) * contrastFactor + 132;
      g = (g - 128) * contrastFactor + 132;
      b = (b - 128) * contrastFactor + 132;
    }

    data[i] = r < 0 ? 0 : r > 255 ? 255 : r;
    data[i + 1] = g < 0 ? 0 : g > 255 ? 255 : g;
    data[i + 2] = b < 0 ? 0 : b > 255 ? 255 : b;
  }

  ctx.putImageData(imgData, 0, 0);
}

async function compressLoadedPdf() {
  if (!loadedPdfDoc || isProcessing) return;
  isProcessing = true;
  recompressBtn.disabled = true;
  downloadBtn.disabled = true;
  progressWrap.hidden = false;

  const targetDpi = Number(dpiInput.value);
  const jpegQuality = Number(qualityInput.value) / 100;
  const boostContrast = contrastBoostInput.checked;
  const makeGrayscale = grayscaleInput.checked;

  // Standard PDF point unit is 72 DPI
  const scale = targetDpi / 72;
  const totalPages = loadedPdfDoc.numPages;

  const outPdf = await PDFDocument.create();
  renderedPagesDataUrls = [];

  const offscreenCanvas = document.createElement('canvas');
  const offscreenCtx = offscreenCanvas.getContext('2d', { willReadFrequently: true });

  for (let pageNum = 1; pageNum <= totalPages; pageNum++) {
    const pct = Math.round(((pageNum - 1) / totalPages) * 100);
    progressText.textContent = `Se optimizează pagina ${pageNum} din ${totalPages}...`;
    progressPercent.textContent = `${pct}%`;
    progressBar.style.width = `${pct}%`;

    const page = await loadedPdfDoc.getPage(pageNum);
    const origViewport = page.getViewport({ scale: 1 });
    const renderViewport = page.getViewport({ scale });

    offscreenCanvas.width = Math.max(1, Math.floor(renderViewport.width));
    offscreenCanvas.height = Math.max(1, Math.floor(renderViewport.height));

    offscreenCtx.fillStyle = '#ffffff';
    offscreenCtx.fillRect(0, 0, offscreenCanvas.width, offscreenCanvas.height);

    await page.render({
      canvasContext: offscreenCtx,
      viewport: renderViewport,
    }).promise;

    applyReadabilityEnhancement(
      offscreenCtx,
      offscreenCanvas.width,
      offscreenCanvas.height,
      boostContrast,
      makeGrayscale
    );

    const jpegDataUrl = offscreenCanvas.toDataURL('image/jpeg', jpegQuality);
    renderedPagesDataUrls.push({
      dataUrl: jpegDataUrl,
      width: offscreenCanvas.width,
      height: offscreenCanvas.height,
    });

    const jpgImage = await outPdf.embedJpg(jpegDataUrl);
    const pdfPage = outPdf.addPage([origViewport.width, origViewport.height]);
    pdfPage.drawImage(jpgImage, {
      x: 0,
      y: 0,
      width: origViewport.width,
      height: origViewport.height,
    });
  }

  progressText.textContent = 'Se finalizează structura PDF...';
  progressPercent.textContent = '100%';
  progressBar.style.width = '100%';

  compressedPdfBytes = await outPdf.save({ useObjectStreams: true });

  const origLen = sourceBytes.byteLength;
  const newLen = compressedPdfBytes.byteLength;
  newSizeVal.textContent = formatBytes(newLen);

  if (newLen < origLen) {
    const savedPct = (((origLen - newLen) / origLen) * 100).toFixed(1);
    savingsVal.textContent = `-${savedPct}% (${formatBytes(origLen - newLen)} economisiți)`;
  } else {
    const diffPct = (((newLen - origLen) / origLen) * 100).toFixed(1);
    savingsVal.textContent = `+${diffPct}% (Scădeți DPI/Calitatea)`;
  }

  updatePreviewDisplay();
  pageNav.hidden = false;
  recompressBtn.disabled = false;
  downloadBtn.disabled = false;
  isProcessing = false;

  setTimeout(() => {
    progressWrap.hidden = true;
  }, 600);
}

function updatePreviewDisplay() {
  if (!renderedPagesDataUrls.length) return;
  emptyPreview.hidden = true;
  previewCanvas.hidden = false;

  if (currentPageIndex >= renderedPagesDataUrls.length) {
    currentPageIndex = renderedPagesDataUrls.length - 1;
  }
  if (currentPageIndex < 0) currentPageIndex = 0;

  const pageObj = renderedPagesDataUrls[currentPageIndex];
  const img = new Image();
  img.onload = () => {
    previewCanvas.width = pageObj.width;
    previewCanvas.height = pageObj.height;
    const ctx = previewCanvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
  };
  img.src = pageObj.dataUrl;

  pageIndicator.textContent = `Pagina ${currentPageIndex + 1} / ${renderedPagesDataUrls.length}`;
  prevPageBtn.disabled = currentPageIndex === 0;
  nextPageBtn.disabled = currentPageIndex === renderedPagesDataUrls.length - 1;
}

prevPageBtn.addEventListener('click', () => {
  if (currentPageIndex > 0) {
    currentPageIndex--;
    updatePreviewDisplay();
  }
});

nextPageBtn.addEventListener('click', () => {
  if (currentPageIndex < renderedPagesDataUrls.length - 1) {
    currentPageIndex++;
    updatePreviewDisplay();
  }
});

toggleZoomBtn.addEventListener('click', () => {
  isActualZoom = !isActualZoom;
  previewCanvas.classList.toggle('zoom-actual', isActualZoom);
  toggleZoomBtn.textContent = isActualZoom ? 'Potrivește în pagină' : 'Zoom 100%';
});

downloadBtn.addEventListener('click', () => {
  if (!compressedPdfBytes || !sourceFile) return;
  const blob = new Blob([compressedPdfBytes], { type: 'application/pdf' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const baseName = sourceFile.name.replace(/\.pdf$/i, '');
  a.href = url;
  a.download = `${baseName}_comprimat.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
});
