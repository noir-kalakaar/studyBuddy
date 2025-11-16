import pytest
import math
from app.rag import split_into_chunks, cosine_similarity


class TestSplitIntoChunks:
    """Tests for split_into_chunks function."""

    def test_empty_string(self):
        """Test splitting an empty string."""
        result = split_into_chunks("")
        assert result == [""]

    def test_single_paragraph_under_limit(self):
        """Test a single paragraph that's under the character limit."""
        text = "This is a short paragraph."
        result = split_into_chunks(text)
        assert result == [text]

    def test_single_paragraph_over_limit(self):
        """Test a single paragraph that exceeds the character limit."""
        text = "A" * 600  # 600 characters, over default 500 limit
        result = split_into_chunks(text)
        assert len(result) == 1
        assert result[0] == text

    def test_multiple_paragraphs_under_limit(self):
        """Test multiple paragraphs that all fit within the limit."""
        text = "First paragraph.\nSecond paragraph.\nThird paragraph."
        result = split_into_chunks(text)
        assert len(result) == 1
        assert result[0] == text

    def test_multiple_paragraphs_split(self):
        """Test multiple paragraphs that need to be split."""
        # Create paragraphs that will exceed 500 chars when combined
        para1 = "A" * 300
        para2 = "B" * 300
        para3 = "C" * 100
        text = f"{para1}\n{para2}\n{para3}"
        
        result = split_into_chunks(text, max_chars=500)
        assert len(result) >= 2
        # First chunk should contain para1
        assert para1 in result[0]
        # Last chunk should contain para3
        assert para3 in result[-1]

    def test_custom_max_chars(self):
        """Test with a custom max_chars parameter."""
        text = "A" * 100 + "\n" + "B" * 100 + "\n" + "C" * 100
        result = split_into_chunks(text, max_chars=150)
        # Should split into multiple chunks since each paragraph is 100 chars
        # and adding them together exceeds 150
        assert len(result) >= 2

    def test_paragraph_exactly_at_limit(self):
        """Test a paragraph that's exactly at the character limit."""
        text = "A" * 500
        result = split_into_chunks(text, max_chars=500)
        assert len(result) == 1
        assert result[0] == text

    def test_paragraph_just_over_limit(self):
        """Test a paragraph that's just over the character limit."""
        text = "A" * 501
        result = split_into_chunks(text, max_chars=500)
        # Should still be one chunk since it's a single paragraph
        assert len(result) == 1

    def test_multiple_empty_lines(self):
        """Test text with multiple empty lines."""
        text = "First\n\n\nSecond\n\nThird"
        result = split_into_chunks(text)
        assert len(result) == 1
        assert "First" in result[0]
        assert "Second" in result[0]
        assert "Third" in result[0]

    def test_preserves_newlines(self):
        """Test that newlines are preserved within chunks."""
        text = "Line 1\nLine 2\nLine 3"
        result = split_into_chunks(text)
        assert "\n" in result[0]
        assert result[0] == text


class TestCosineSimilarity:
    """Tests for cosine_similarity function."""

    def test_identical_vectors(self):
        """Test cosine similarity of identical vectors."""
        vec = [1.0, 2.0, 3.0]
        result = cosine_similarity(vec, vec)
        assert result == pytest.approx(1.0, abs=1e-9)

    def test_orthogonal_vectors(self):
        """Test cosine similarity of orthogonal vectors (should be 0)."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        result = cosine_similarity(vec1, vec2)
        assert result == pytest.approx(0.0, abs=1e-9)

    def test_opposite_vectors(self):
        """Test cosine similarity of opposite vectors (should be -1)."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]
        result = cosine_similarity(vec1, vec2)
        assert result == pytest.approx(-1.0, abs=1e-9)

    def test_zero_vector(self):
        """Test cosine similarity with zero vector."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [0.0, 0.0, 0.0]
        result = cosine_similarity(vec1, vec2)
        assert result == 0.0

    def test_both_zero_vectors(self):
        """Test cosine similarity with both vectors being zero."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [0.0, 0.0, 0.0]
        result = cosine_similarity(vec1, vec2)
        assert result == 0.0

    def test_positive_similarity(self):
        """Test vectors with positive similarity."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 1.0, 0.0]
        result = cosine_similarity(vec1, vec2)
        # Should be positive and less than 1
        assert 0 < result < 1
        # cos(45°) = 1/√2 ≈ 0.707
        expected = 1.0 / math.sqrt(2)
        assert result == pytest.approx(expected, abs=1e-9)

    def test_negative_similarity(self):
        """Test vectors with negative similarity."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [-1.0, 1.0, 0.0]
        result = cosine_similarity(vec1, vec2)
        # Should be negative
        assert result < 0
        # cos(135°) = -1/√2 ≈ -0.707
        expected = -1.0 / math.sqrt(2)
        assert result == pytest.approx(expected, abs=1e-9)

    def test_different_length_vectors(self):
        """Test that function handles vectors of different lengths."""
        vec1 = [1.0, 2.0]
        vec2 = [1.0, 2.0, 3.0]
        # zip will only use first 2 elements for dot product
        # Dot product: 1*1 + 2*2 = 5
        # Norm vec1: sqrt(1^2 + 2^2) = sqrt(5)
        # Norm vec2: sqrt(1^2 + 2^2 + 3^2) = sqrt(14)
        # Result: 5 / (sqrt(5) * sqrt(14)) = 5 / sqrt(70)
        result = cosine_similarity(vec1, vec2)
        expected = 5.0 / math.sqrt(5 * 14)
        assert result == pytest.approx(expected, abs=1e-9)

    def test_unit_vectors(self):
        """Test with unit vectors."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 0.0, 1.0]
        result = cosine_similarity(vec1, vec2)
        assert result == pytest.approx(0.0, abs=1e-9)

    def test_high_dimensional_vectors(self):
        """Test with high-dimensional vectors."""
        vec1 = [1.0] * 100
        vec2 = [1.0] * 100
        result = cosine_similarity(vec1, vec2)
        assert result == pytest.approx(1.0, abs=1e-9)

    def test_negative_values(self):
        """Test with vectors containing negative values."""
        vec1 = [-1.0, 2.0, -3.0]
        vec2 = [1.0, -2.0, 3.0]
        result = cosine_similarity(vec1, vec2)
        # Dot product: -1*1 + 2*(-2) + (-3)*3 = -1 - 4 - 9 = -14
        # Norms: sqrt(1+4+9) = sqrt(14) for both
        # Result: -14 / (sqrt(14) * sqrt(14)) = -14 / 14 = -1
        assert result == pytest.approx(-1.0, abs=1e-9)

    def test_single_element_vectors(self):
        """Test with single-element vectors."""
        vec1 = [5.0]
        vec2 = [3.0]
        result = cosine_similarity(vec1, vec2)
        # Both point in same direction, should be 1
        assert result == pytest.approx(1.0, abs=1e-9)

    def test_float_precision(self):
        """Test with floating point values."""
        vec1 = [0.1, 0.2, 0.3]
        vec2 = [0.4, 0.5, 0.6]
        result = cosine_similarity(vec1, vec2)
        # Should be a valid cosine similarity value between -1 and 1
        assert -1.0 <= result <= 1.0
        assert isinstance(result, float)

