import base64
import io
import os
from glob import glob
from typing import Dict, List, Optional, Tuple

import cv2
import joblib
import numpy as np
import pandas as pd
import sklearn
import torch
from PIL import Image
from scipy.special import softmax
from skimage.feature import hog
from skimage.transform import resize
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
from transformers import CLIPModel, CLIPProcessor

from lexoid.core.conversion_utils import convert_doc_to_base64_images, cv2_to_pil

# ====================== Image Feature Extraction ======================


def base64_to_cv2_image(b64_string: str) -> np.ndarray:
    image_data = base64.b64decode(b64_string.split(",")[1])
    image = Image.open(io.BytesIO(image_data)).convert("L")  # grayscale
    return np.array(image)


def extract_edge_stats(edges: np.ndarray) -> Tuple[float, float, float, float]:
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    lengths = []
    angles = []

    for contour in contours:
        for i in range(1, len(contour)):
            p1 = contour[i - 1][0]
            p2 = contour[i][0]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = np.hypot(dx, dy)
            if length == 0:
                continue
            angle = np.degrees(np.arctan2(dy, dx))
            lengths.append(length)
            angles.append(angle)

    if not lengths:
        return 0.0, 0.0, 0.0, 0.0

    return (np.mean(lengths), np.var(lengths), np.mean(angles), np.var(angles))


def extract_hog_features(
    image: np.ndarray, resize_shape=(128, 128)
) -> Tuple[float, float]:
    """
    Extracts summary HOG features from an image.

    Returns:
        Tuple of (mean, variance) of the HOG feature vector.
    """
    resized = resize(image, resize_shape, anti_aliasing=True)
    features = hog(
        resized,
        orientations=9,
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2),
        block_norm="L2-Hys",
        feature_vector=True,
    )
    return np.mean(features), np.var(features)


def extract_page_features(img: np.ndarray) -> List[float]:
    h, w = img.shape
    aspect_ratio = w / h

    # Binarization
    _, bin_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text_pixels = np.sum(bin_img < 128)
    text_density = text_pixels / (h * w)

    # Line estimation
    horizontal_projection = np.sum(bin_img < 128, axis=1)
    lines = np.sum(horizontal_projection > 0.5 * np.max(horizontal_projection))

    # Noise (Canny)
    edges = cv2.Canny(img, 100, 200)
    noise_level = np.sum(edges) / 255 / (h * w)

    # Skew angle
    coords = np.column_stack(np.where(bin_img < 128))
    angle = 0.0
    if len(coords) > 0:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle += 90

    # Edge stats
    mean_len, var_len, mean_ang, var_ang = extract_edge_stats(edges)

    # HOG features
    hog_mean, hog_var = extract_hog_features(img)

    return [
        text_density,
        lines,
        noise_level,
        aspect_ratio,
        angle,
        mean_len,
        var_len,
        mean_ang,
        var_ang,
        hog_mean,
        hog_var,
    ]


def extract_doc_features(doc_path: str) -> List[float]:
    page_data = convert_doc_to_base64_images(doc_path)
    features = [extract_page_features(base64_to_cv2_image(b64)) for _, b64 in page_data]
    features = np.array(features)
    return features.mean(axis=0)


def extract_image_embedding(
    image_path: str,
    model: Optional[CLIPModel] = None,
    processor: Optional[CLIPProcessor] = None,
    device: str = "cpu",
) -> np.ndarray:
    """Extract embedding using CLIP, converting PDFs to images if needed."""
    if model is None or processor is None:
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    # Convert document to images
    page_data = convert_doc_to_base64_images(
        image_path
    )  # List of (page_num, base64_img)
    embeddings = []

    for _, b64 in page_data:
        cv2_img = base64_to_cv2_image(b64)
        pil_img = cv2_to_pil(cv2_img)
        inputs = processor(images=pil_img, return_tensors="pt").to(device)

        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
        embeddings.append(image_features.cpu().numpy())

    # Average embeddings across pages
    embeddings = np.vstack(embeddings)
    final_embedding = embeddings.mean(axis=0).flatten()

    if model is None and processor is None:
        del model
        del processor
        torch.cuda.empty_cache()

    return final_embedding


def extract_features(
    path: str, use_image: bool = False, model=None, processor=None, device="cpu"
) -> np.ndarray:
    if use_image:
        return extract_image_embedding(
            path, model=model, processor=processor, device=device
        )
    else:
        return extract_doc_features(path)


# ====================== Model Training and Inference ======================


class LLMSelector:
    """Base class for LLM selectors."""

    def __init__(
        self, results_csv: str, doc_dir: str, model_dir: str, classification: bool
    ):
        self.results_csv = results_csv
        self.doc_dir = doc_dir
        self.model_dir = model_dir
        self.fitted = False
        self.feature_path = os.path.join(model_dir, "features.npy")
        self.target_path = os.path.join(model_dir, "targets.npy")
        self.model_path = os.path.join(model_dir, "model.pkl")
        self.scaler_path = os.path.join(model_dir, "scaler.pkl")
        self.model_list_path = os.path.join(model_dir, "models.txt")
        os.makedirs(model_dir, exist_ok=True)
        self.models = []
        self.classification = classification
        self.scaler = StandardScaler()

    def train(self):
        X, Y = self._prepare_data()
        X_scaled = self.scaler.fit_transform(X)
        if self.classification:
            Y = Y.argmax(axis=1)

        self.model.fit(X_scaled, Y)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        np.save(self.feature_path, X)
        np.save(self.target_path, Y)
        self.fitted = True
        print("Model trained and saved.")

    def _prepare_data(self):
        df = pd.read_csv(self.results_csv)

        self.models = sorted(df["model"].unique().tolist())
        with open(self.model_list_path, "w") as f:
            f.write("\n".join(self.models))

        grouped = df.groupby("Input File")

        X, Y = [], []
        for base_name, group in tqdm(grouped):
            path = glob(os.path.join(self.doc_dir, base_name + "*"))[0]
            features = extract_doc_features(path)
            labels = (
                group.set_index("model")["sequence_matcher"]
                .reindex(self.models)
                .fillna(0.0)
                .values
            )
            X.append(features)
            Y.append(labels)
        X, Y = np.array(X), np.array(Y)
        return X, Y

    def load(self):
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        with open(self.model_list_path) as f:
            self.models = [line.strip() for line in f.readlines()]
        self.fitted = True

    def predict_scores(self, x: str | np.ndarray) -> Dict[str, float]:
        if not self.fitted:
            self.load()
        if isinstance(x, str):
            features = extract_doc_features(x)
        else:
            features = x
        X_scaled = self.scaler.transform([features])
        if self.classification:
            scores = self.model.predict_proba(X_scaled)
        else:
            scores = self.model.predict(X_scaled)

        return dict(zip(self.models, scores[0]))

    def evaluate_leave_one_out(self) -> pd.DataFrame:
        print("Running Leave-One-Out Cross-Validation...")
        X, Y = self._prepare_data()
        n_docs = X.shape[0]
        all_predictions = []
        all_targets = []

        for i in range(n_docs):
            # Split into train/test
            X_train = np.delete(X, i, axis=0)
            Y_train = np.delete(Y, i, axis=0)
            X_test = X[i].reshape(1, -1)
            Y_test = Y[i]

            # Fit model on train split
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            if self.classification:
                Y_train = Y_train.argmax(axis=1)
                Y_test = Y_test.argmax()
            model = self.model_fn()
            model.fit(X_train_scaled, Y_train)

            # Predict on left-out doc
            Y_pred = model.predict(X_test_scaled)[0]
            all_predictions.append(Y_pred)
            all_targets.append(Y_test)

        predictions = np.array(all_predictions)
        targets = np.array(all_targets)

        # Compute mean absolute error per model
        error = self.error_fn(predictions, targets)

        print(f"Overall Mean Error: {error:.4f}")

    def evaluate_on_train(self) -> pd.DataFrame:
        if not self.fitted:
            self.load()
        X, Y = np.load(self.feature_path), np.load(self.target_path)
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        error = self.error_fn(predictions, Y)
        print(f"Training Set Error: {error}")


class LLMScoreRegressor(LLMSelector):
    """Use regression models to predict similarity scores for each LLM."""

    def __init__(
        self,
        results_csv="tests/outputs/document_results.csv",
        doc_dir="examples/inputs/",
        model_dir="model_data",
        regression_model: callable = lambda: sklearn.linear_model.LassoLars(
            alpha=0.4, random_state=42
        ),
    ):
        super().__init__(results_csv, doc_dir, model_dir, classification=False)
        self.regression_model = regression_model
        self.model_fn = lambda: MultiOutputRegressor(regression_model())
        self.model = self.model_fn()
        self.error_fn = lambda predictions, targets: (
            np.mean(np.abs(predictions - targets))
        )

    def rank_models(self, doc_path: str) -> List[Tuple[str, float]]:
        scores = self.predict_scores(doc_path)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)


class LLMClassifier(LLMSelector):
    """Use a classification model to predict the best LLM for a document."""

    def __init__(
        self,
        results_csv="tests/outputs/document_results.csv",
        doc_dir="examples/inputs/",
        model_dir="model_data",
        classification_model: callable = lambda: sklearn.linear_model.LogisticRegression(
            max_iter=1000, random_state=42
        ),
    ):
        super().__init__(results_csv, doc_dir, model_dir, classification=True)
        self.model_fn = self.classification_model = classification_model
        self.model = classification_model()
        self.classification = True
        self.error_fn = lambda predictions, targets: 1 - (
            np.mean(predictions == targets, axis=0)
        )

    def rank_models(self, doc_path: str) -> List[Tuple[str, float]]:
        scores = self.predict_scores(doc_path)
        ranked_models = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(model, score) for model, score in ranked_models if score > 0]


class DocumentRankedLLMSelector:
    """
    Ranks documents by similarity and uses top-k to recommend LLMs.
    """

    def __init__(
        self,
        results_csv="tests/outputs/document_results.csv",
        doc_dir="examples/inputs/",
        model_dir="model_data",
        use_image_embeddings: bool = False,
        device: str = "cpu",
    ):
        self.results_csv = results_csv
        self.doc_dir = doc_dir
        self.model_dir = model_dir
        self.use_image_embeddings = use_image_embeddings
        self.device = device

        os.makedirs(model_dir, exist_ok=True)
        self.embed_path = os.path.join(model_dir, "doc_embeddings.npy")
        self.name_path = os.path.join(model_dir, "doc_names.npy")
        self.scaler_path = os.path.join(model_dir, "scaler.pkl")
        if use_image_embeddings:
            self.embed_path = os.path.join(model_dir, "doc_image_embeddings.npy")
            self.scaler_path = os.path.join(model_dir, "image_scaler.pkl")
        self.scaler = StandardScaler()

        self.embeddings = None
        self.doc_names = None
        self.model = None
        self.processor = None

        self._load_or_build_doc_embeddings()
        print(f"Loaded {len(self.doc_names)} document embeddings.")

    def _load_or_build_doc_embeddings(self):
        """Load or compute and save document embeddings."""
        if os.path.exists(self.embed_path) and os.path.exists(self.name_path):
            self.embeddings = np.load(self.embed_path)
            self.doc_names = np.load(self.name_path, allow_pickle=True).tolist()
            self.scaler = joblib.load(self.scaler_path)
            return

        print("Extracting and saving document embeddings...")
        df = pd.read_csv(self.results_csv)
        grouped = df.groupby("Input File")
        self.doc_names = []
        self.embeddings = []

        if self.use_image_embeddings:
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(
                self.device
            )
            self.processor = CLIPProcessor.from_pretrained(
                "openai/clip-vit-base-patch32"
            )

        for base_name, _ in tqdm(grouped):
            path = sorted(glob(os.path.join(self.doc_dir, base_name + "*")))[0]
            features = extract_features(
                path,
                use_image=self.use_image_embeddings,
                model=self.model,
                processor=self.processor,
                device=self.device,
            )
            self.embeddings.append(features)
            self.doc_names.append(base_name)

        print(f"Extracted {len(self.doc_names)} document embeddings.")

        self.embeddings = np.array(self.embeddings)
        self.embeddings = self.scaler.fit_transform(self.embeddings)

        np.save(self.embed_path, self.embeddings)
        np.save(self.name_path, self.doc_names)
        joblib.dump(self.scaler, self.scaler_path)

    def rank_documents(self, query_path: str) -> List[Tuple[str, float]]:
        """Return top-k similar documents to the given document."""
        query_vec = extract_features(
            query_path,
            use_image=self.use_image_embeddings,
            model=self.model,
            processor=self.processor,
            device=self.device,
        ).reshape(1, -1)
        query_vec = self.scaler.transform(query_vec)
        sims = cosine_similarity(query_vec, self.embeddings)[0]

        ranked = sorted(zip(self.doc_names, sims), key=lambda x: x[1], reverse=True)
        print(f"Ranked documents: {ranked}")
        return ranked

    def rank_models(self, query_path: str) -> List[Tuple[str, float]]:
        # Step 1: Find the most similar document
        top_docs = self.rank_documents(query_path)
        most_similar_doc, similarity = top_docs[0]
        print(
            f"Most similar document to {query_path}: {most_similar_doc} (sim={similarity:.4f})"
        )

        # Step 2: Load model results for that document
        df = pd.read_csv(self.results_csv)
        doc_df = df[df["Input File"] == most_similar_doc]

        if doc_df.empty:
            raise ValueError(f"No model scores found for document: {most_similar_doc}")

        # Step 3: Extract and return model scores sorted by descending score
        model_scores = list(
            doc_df[["model", "sequence_matcher"]]
            .sort_values(by="sequence_matcher", ascending=False)
            .itertuples(index=False, name=None)
        )

        return model_scores

    def weighted_rank_models(self, query_path: str) -> List[Tuple[str, float]]:
        # Step 1: Get top-K similar documents
        top_docs = self.rank_documents(query_path)  # List of (doc_name, similarity)
        print(f"Top documents for {query_path}: {top_docs}")
        doc_names, similarities = zip(*top_docs)

        # Step 2: Normalize the similarities for weighting
        weights = softmax(similarities)

        # Step 3: Load results and filter to top-k documents
        df = pd.read_csv(self.results_csv)
        df = df[df["Input File"].isin(doc_names)]

        # Step 4: Build a matrix of [doc x model] scores
        models = df["model"].unique()
        score_matrix = {model: 0.0 for model in models}
        weight_sums = {model: 0.0 for model in models}

        for i, doc in enumerate(doc_names):
            doc_df = df[df["Input File"] == doc]
            for _, row in doc_df.iterrows():
                model = row["model"]
                score = row["sequence_matcher"]
                score_matrix[model] += score * weights[i]
                weight_sums[model] += weights[i]

        # Step 5: Compute weighted averages
        final_scores = {
            model: (
                score_matrix[model] / weight_sums[model]
                if weight_sums[model] > 0
                else 0.0
            )
            for model in models
        }

        # Step 6: Return sorted model rankings
        return sorted(final_scores.items(), key=lambda x: x[1], reverse=True)


# ====================== Example Usage ======================

if __name__ == "__main__":
    model_dir = "lexoid/core/model_data"
    # task_type = "classification"

    # if task_type == "classification":

    #     def classifier_fn():
    #         return sklearn.neighbors.KNeighborsClassifier(n_neighbors=1)

    #     selector = LLMClassifier(
    #         model_dir=model_dir, classification_model=classifier_fn
    #     )
    # else:

    #     def regressor_fn():
    #         return sklearn.linear_model.LassoLars(alpha=0.4, random_state=42)

    #     selector = LLMScoreRegressor(model_dir=model_dir, regression_model=regressor_fn)

    # selector.train()
    # # selector.evaluate_leave_one_out()
    # selector.evaluate_on_train()

    # test_doc = "examples/inputs/test_2.pdf"
    # ranking = selector.rank_models(test_doc)
    # print("Model Ranking:")
    # for model, score in ranking:
    #     print(f"{model}: {score:.4f}")

    doc_selector = DocumentRankedLLMSelector(
        results_csv="tests/outputs/document_results.csv",
        doc_dir="examples/inputs/",
        model_dir=model_dir,
        use_image_embeddings=True,
        device="cpu",
    )
    query_doc = "examples/inputs/medical_invoice_sample1.png"
    ranked_docs = doc_selector.rank_models(query_doc)
    print("Ranked Documents:")
    for doc, score in ranked_docs:
        print(f"{doc}: {score:.4f}")
