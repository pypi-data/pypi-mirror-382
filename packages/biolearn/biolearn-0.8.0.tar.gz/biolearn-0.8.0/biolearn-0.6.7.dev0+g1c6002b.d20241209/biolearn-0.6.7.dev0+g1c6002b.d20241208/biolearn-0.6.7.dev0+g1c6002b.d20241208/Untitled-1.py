
    def save_to_hdf5(self, filepath, complevel=9, complib="zlib"):
        """
        Saves the GeoData instance to an HDF5 file with compression.
        """
        with pd.HDFStore(
            filepath, mode="w", complevel=complevel, complib=complib
        ) as store:
            if hasattr(self, "metadata") and self.metadata is not None:
                store.put("metadata", self.metadata, format="table")
            if hasattr(self, "dnam") and self.dnam is not None:
                store.put("dnam", self.dnam, format="table")
            if hasattr(self, "rna") and self.rna is not None:
                store.put("rna", self.rna, format="table")
            if hasattr(self, "protein") and self.protein is not None:
                store.put("protein", self.protein, format="table")

    def save_to_csv(self, base_filepath):
        """
        Saves each attribute of the GeoData instance to a separate CSV file.
        """
        if hasattr(self, "metadata") and self.metadata is not None:
            self.metadata.to_csv(f"{base_filepath}_metadata.csv", index=False)
        if hasattr(self, "dnam") and self.dnam is not None:
            self.dnam.to_csv(f"{base_filepath}_dnam.csv", index=False)
        if hasattr(self, "rna") and self.rna is not None:
            self.rna.to_csv(f"{base_filepath}_rna.csv", index=False)
        if hasattr(self, "protein") and self.protein is not None:
            self.protein.to_csv(f"{base_filepath}_protein.csv", index=False)

    def load_from_hdf5(self, filepath):
        """
        Loads the GeoData instance from an HDF5 file.

        Args:
            filepath (str): The path to the HDF5 file to load the data from.
        """
        with pd.HDFStore(filepath, mode="r") as store:
            # Load each DataFrame from the HDF5 store
            self.metadata = (
                store.get("metadata") if "metadata" in store else None
            )
            self.dnam = store.get("dnam") if "dnam" in store else None
            self.rna = store.get("rna") if "rna" in store else None
            self.protein = store.get("protein") if "protein" in store else None

,
  "tables"