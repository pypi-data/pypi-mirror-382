"""Database path configuration for AMR detection tools."""

import sys
from pathlib import Path

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files


def get_database_path(database_name: str, tool: str) -> str:

    try:
        # Get the package's databases directory
        db_root = files('your_package_name').joinpath('databases')

        if database_name.lower() == 'card':
            db_paths = {
                "diamond": db_root / "card/diamond/protein_fasta_protein_homolog_model_SID_diamonddb.dmnd",
                "blastn": db_root / "card/blast_dna/nucleotide_fasta_protein_homolog_model_SID_blastdb",
                "blastp": db_root / "card/blast_aa/protein_fasta_protein_homolog_model_SID_blastdb",
                "bowtie2": db_root / "card/bowtie2/nucleotide_fasta_protein_homolog_model_SID_bowtie2db",
                "bwa": db_root / "card/bwa/nucleotide_fasta_protein_homolog_model_SID_bwadb",
                "minimap2": db_root / "card/minimap2/nucleotide_fasta_protein_homolog_model_SID_minimap2db",
            }
        elif database_name.lower() == 'resfinder':
            db_paths = {
                "diamond": db_root / "resfinder/diamond/all_aa_diamonddb.dmnd",
                "blastn": db_root / "resfinder/blast_dna/all_blastdb",
                "blastp": db_root / "resfinder/blast_aa/all_aa_blastdb",
                "bowtie2": db_root / "resfinder/bowtie2/all_bowtie2db",
                "bwa": db_root / "resfinder/bwa/all_bwadb",
                "minimap2": db_root / "resfinder/minimap2/all_minimap2db",
            }
        else:
            return None

        path = db_paths.get(tool)
        return str(path) if path else None

    except Exception:
        # Fallback for development/local running
        package_dir = Path(__file__).parent
        db_root = package_dir / 'databases'

        if database_name.lower() == 'card':
            db_paths = {
                "diamond": "card/diamond/protein_fasta_protein_homolog_model_SID_diamonddb.dmnd",
                "blastn": "card/blast_dna/nucleotide_fasta_protein_homolog_model_SID_blastdb",
                "blastp": "card/blast_aa/protein_fasta_protein_homolog_model_SID_blastdb",
                "bowtie2": "card/bowtie2/nucleotide_fasta_protein_homolog_model_SID_bowtie2db",
                "bwa": "card/bwa/nucleotide_fasta_protein_homolog_model_SID_bwadb",
                "minimap2": "card/minimap2/nucleotide_fasta_protein_homolog_model_SID_minimap2db",
            }
        else:  # resfinder
            db_paths = {
                "diamond": "resfinder/diamond/all_aa_diamonddb.dmnd",
                "blastn": "resfinder/blast_dna/all_blastdb",
                "blastp": "resfinder/blast_aa/all_aa_blastdb",
                "bowtie2": "resfinder/bowtie2/all_bowtie2db",
                "bwa": "resfinder/bwa/all_bwadb",
                "minimap2": "resfinder/minimap2/all_minimap2db",
            }

        rel_path = db_paths.get(tool)
        return str(db_root / rel_path) if rel_path else None



CARD_DATABASES = {
    "diamond": get_database_path('card', 'diamond'),
    "blastn": get_database_path('card', 'blastn'),
    "blastp": get_database_path('card', 'blastp'),
    "bowtie2": get_database_path('card', 'bowtie2'),
    "bwa": get_database_path('card', 'bwa'),
    "minimap2": get_database_path('card', 'minimap2'),
}

RESFINDER_DATABASES = {
    "diamond": get_database_path('resfinder', 'diamond'),
    "blastn": get_database_path('resfinder', 'blastn'),
    "blastp": get_database_path('resfinder', 'blastp'),
    "bowtie2": get_database_path('resfinder', 'bowtie2'),
    "bwa": get_database_path('resfinder', 'bwa'),
    "minimap2": get_database_path('resfinder', 'minimap2'),
}