//useState to track and grab image urls
import { useState } from "react";

function App() {
  //image1 2 stores actual photos, preview1 2 stores the preview urls
  const [image1, setImage1] = useState<File | null>(null);
  const [image2, setImage2] = useState<File | null>(null);
  const [preview1, setPreview1] = useState<string | null>(null);
  const [preview2, setPreview2] = useState<string | null>(null);
  const [similarity, setSimilarity] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<"overlay" | "heatmap" | "grayscale">("overlay");
  const [diffs, setDiffs] = useState<{ [key: string]: string }>({});
  const [aiSimilarity, setAiSimilarity] = useState<number | null>(null);
  const [hybridSimilarity, setHybridSimilarity] = useState<number | null>(null);
  const [differenceReason, setDifferenceReason] = useState<string | null>(null);
  const [threshold, setThreshold] = useState(0.85);


  //function to handle image change
  const handleImageChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    index: number
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const previewURL = URL.createObjectURL(file);
    if (index === 1) {
      setImage1(file);
      setPreview1(previewURL);
    } else {
      setImage2(file);
      setPreview2(previewURL);
    }
  };

  const handleCompare = async() => {
    if (!image1 || !image2) return;

    const formData = new FormData();
    formData.append("file1", image1);
    formData.append("file2", image2);

    try {
      const response = await fetch(`http://localhost:8000/compare?threshold=${threshold}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      console.log("Backend response:", data);
      setSimilarity(data.similarity);
      setAiSimilarity(data.ai_similarity);
      setHybridSimilarity(data.hybrid_similarity);
      setDifferenceReason(data.difference_reason);
      setDiffs({
        overlay: data.diff_overlay,
        heatmap: data.diff_heatmap,
        grayscale: data.diff_grayscale
      });
    } catch (error) {
      console.error("Error comparing images:", error);
    }
  }

return (
  <div className="min-h-screen w-full bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center px-4">
    <div className="w-full max-w-5xl bg-white p-8 rounded-lg shadow-lg">
      <h1 className="text-4xl font-bold text-slate-800 mb-2 text-center">SnapCompare</h1>
      <p className="text-slate-600 mb-8 text-center">
        Upload two images to compare their similarity.
      </p>

      {/* Image upload section */}
      <div className="flex flex-col sm:flex-row justify-center gap-8 mb-8">
        {/* Image 1 */}
        <div className="flex flex-col items-center">
          <label className="text-sm font-semibold text-slate-700 mb-2">Image 1</label>
          <input type="file" accept="image/*" onChange={(e) => handleImageChange(e, 1)} />
          {preview1 && (
            <img
              src={preview1}
              alt="Preview 1"
              className="mt-4 rounded-md border border-slate-300 shadow-md w-64"
            />
          )}
        </div>

        {/* Image 2 */}
        <div className="flex flex-col items-center">
          <label className="text-sm font-semibold text-slate-700 mb-2">Image 2</label>
          <input type="file" accept="image/*" onChange={(e) => handleImageChange(e, 2)} />
          {preview2 && (
            <img
              src={preview2}
              alt="Preview 2"
              className="mt-4 rounded-md border border-slate-300 shadow-md w-64"
            />
          )}
        </div>
      </div>

      {/* Compare button */}
      <div className="text-center">
        <button
          disabled={!image1 || !image2}
          onClick={handleCompare}
          className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium px-6 py-2 rounded transition disabled:opacity-40"
        >
          Compare Images
        </button>
      </div>
      {/* Threshold Input */}
      <div className="mt-6 text-center">
        <label className="block mb-2 font-medium text-slate-700">
          Difference Map Sensitivity Threshold: {threshold.toFixed(2)}
        </label>
        <input
          type="range"
          min="0.5"
          max="0.99"
          step="0.01"
          value={threshold}
          onChange={(e) => setThreshold(parseFloat(e.target.value))}
          className="w-64"
        />
      </div>
      {/* Similarity Score Result */}
      {similarity !== null && (
        <div className="mt-8 bg-slate-50 border border-slate-200 p-6 rounded-md shadow-md text-center">
          <p className="text-xl font-semibold text-slate-800">
            Similarity Score:{" "}
            <span className="text-emerald-600 font-bold">{similarity}</span>
          </p>
        </div>
      )}

      {/* AI Similarity Score Result */}
      {aiSimilarity !== null && (
        <div className="mt-8 bg-slate-50 border border-slate-200 p-6 rounded-md shadow-md text-center">
          <p className="text-xl font-semibold text-slate-800">
            Ai similarity Score:{" "}
            <span className="text-emerald-600 font-bold">{aiSimilarity}</span>
          </p>
        </div>
      )}
      {/* Hybrid Similarity Score Result */}
      {hybridSimilarity !== null && (
        <div className="mt-4 bg-white p-4 rounded shadow-md text-center">
          <p className="text-xl font-semibold text-slate-800">
            Overall Similarity Score:{" "}
            <span className="text-teal-600 font-bold">{hybridSimilarity}</span>
          </p>
        </div>
      )}
      {/* Difference Reason Result */}
      {differenceReason && (
        <div className="mt-4 bg-slate-100 p-4 rounded shadow text-center text-slate-700">
          <p className="italic">AI Interpretation: {differenceReason}</p>
        </div>
      )}
      {/* View Mode Selection */}
        <div className="flex justify-center gap-4 mt-6">
          <button onClick={() => setViewMode("overlay")} className="px-4 py-1 rounded bg-slate-200 hover:bg-slate-300">Overlay</button>
          <button onClick={() => setViewMode("heatmap")} className="px-4 py-1 rounded bg-slate-200 hover:bg-slate-300">Heatmap</button>
          <button onClick={() => setViewMode("grayscale")} className="px-4 py-1 rounded bg-slate-200 hover:bg-slate-300">Grayscale</button>
        </div>
      {/* Difference Image Result */}
      {diffs[viewMode] && (
        <div className="text-center mt-4">
          <h3 className="text-lg font-semibold mb-2 text-slate-700">
            Visual Difference Map ({viewMode})
          </h3>
          <img
            src={`data:image/png;base64,${diffs[viewMode]}`}
            alt="Difference map"
            className="mx-auto border rounded shadow"
          />
        </div>
      )}
    </div>
  </div>
);

}

export default App;
