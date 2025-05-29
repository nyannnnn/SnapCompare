//useState to track and grab image urls
import { useState } from "react";

function App() {
  //image1 2 stores actual photos, preview1 2 stores the preview urls
  const [image1, setImage1] = useState<File | null>(null);
  const [image2, setImage2] = useState<File | null>(null);
  const [preview1, setPreview1] = useState<string | null>(null);
  const [preview2, setPreview2] = useState<string | null>(null);

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

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>SnapCompare</h1>
      <p>Upload two images to compare them visually and semantically.</p>

      <div style={{ marginTop: "2rem" }}>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => handleImageChange(e, 1)}
        />
        {preview1 && <img src={preview1} alt="Image 1 preview" width={200} />}
      </div>

      <div style={{ marginTop: "1rem" }}>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => handleImageChange(e, 2)}
        />
        {preview2 && <img src={preview2} alt="Image 2 preview" width={200} />}
      </div>

      <div className="text-3xl font-bold underline text-blue-600">
        Tailwind is working!
      </div>

      <div style={{ marginTop: "2rem" }}>
        <button
          disabled={!image1 || !image2}
          onClick={() => console.log("TODO: send to backend")}
        >
          Compare Images
        </button>
      </div>
    </div>
  );
}

export default App;
