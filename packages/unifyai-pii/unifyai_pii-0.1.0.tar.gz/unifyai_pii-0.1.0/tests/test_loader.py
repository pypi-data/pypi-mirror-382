"""Tests for the country recognizer loader."""  
  
import pytest  
from presidio_analyzer import AnalyzerEngine, EntityRecognizer  
from unifyai_pii import (  
    load_country_recognizers,  
    get_supported_countries,  
    get_country_entity_types,  
    create_analyzer_with_countries,  
    add_country_recognizers_to_analyzer,  
)  
  

class TestLoadCountryRecognizers:  
    """Test suite for load_country_recognizers function."""  
  
    def test_load_india_recognizers(self):  
        """Test loading Indian PII recognizers."""  
        recognizers = load_country_recognizers("IN")  
          
        assert len(recognizers) == 5  
        assert all(isinstance(r, EntityRecognizer) for r in recognizers)  
          
        # Verify entity types  
        entity_types = set()  
        for rec in recognizers:  
            entity_types.update(rec.supported_entities)  
          
        expected_entities = {  
            "IN_AADHAAR",  
            "IN_PAN",  
            "IN_PASSPORT",  
            "IN_VEHICLE_REGISTRATION",  
            "IN_VOTER",  
        }  
        assert entity_types == expected_entities  
  
    def test_load_usa_recognizers(self):  
        """Test loading USA PII recognizers."""  
        recognizers = load_country_recognizers("US")  
          
        assert len(recognizers) == 5  
          
        entity_types = set()  
        for rec in recognizers:  
            entity_types.update(rec.supported_entities)  
          
        expected_entities = {  
            "US_SSN",  
            "US_PASSPORT",  
            "US_DRIVER_LICENSE",  
            "US_ITIN",  
            "US_BANK_NUMBER",  
        }  
        assert entity_types == expected_entities  
  
    def test_load_uk_recognizers(self):  
        """Test loading UK PII recognizers."""  
        recognizers = load_country_recognizers("UK")  
          
        assert len(recognizers) == 2  
          
        entity_types = set()  
        for rec in recognizers:  
            entity_types.update(rec.supported_entities)  
          
        expected_entities = {"UK_NHS", "UK_NINO"}  
        assert entity_types == expected_entities  
  
    def test_country_code_case_insensitive(self):  
        """Test that country codes are case-insensitive."""  
        recognizers_upper = load_country_recognizers("IN")  
        recognizers_lower = load_country_recognizers("in")  
          
        assert len(recognizers_upper) == len(recognizers_lower)  
  
    def test_invalid_country_code_raises_error(self):  
        """Test that invalid country code raises ValueError."""  
        with pytest.raises(ValueError, match="Country code 'XX' not supported"):  
            load_country_recognizers("XX")  
  
    def test_country_alias_gb_for_uk(self):  
        """Test that GB is an alias for UK."""  
        recognizers_uk = load_country_recognizers("UK")  
        recognizers_gb = load_country_recognizers("GB")  
          
        assert len(recognizers_uk) == len(recognizers_gb)  
  
  
class TestGetSupportedCountries:  
    """Test suite for get_supported_countries function."""  
  
    def test_returns_sorted_list(self):  
        """Test that supported countries are returned as sorted list."""  
        countries = get_supported_countries()  
          
        assert isinstance(countries, list)  
        assert len(countries) > 0  
        assert countries == sorted(countries)  
  
    def test_contains_expected_countries(self):  
        """Test that expected countries are in the list."""  
        countries = get_supported_countries()  
          
        expected = ["IN", "US", "UK", "ES", "IT", "AU", "SG", "PL", "FI"]  
        for country in expected:  
            assert country in countries  
  
  
class TestGetCountryEntityTypes:  
    """Test suite for get_country_entity_types function."""  
  
    def test_get_india_entity_types(self):  
        """Test getting entity types for India."""  
        entity_types = get_country_entity_types("IN")  
          
        assert isinstance(entity_types, list)  
        assert "IN_AADHAAR" in entity_types  
        assert "IN_PAN" in entity_types  
  
    def test_invalid_country_raises_error(self):  
        """Test that invalid country code raises ValueError."""  
        with pytest.raises(ValueError, match="Country code 'XX' not supported"):  
            get_country_entity_types("XX")  
  
  
class TestCreateAnalyzerWithCountries:  
    """Test suite for create_analyzer_with_countries function."""  
  
    def test_create_analyzer_single_country(self):  
        """Test creating analyzer with single country."""  
        analyzer = create_analyzer_with_countries(["IN"])  
          
        assert isinstance(analyzer, AnalyzerEngine)  
          
        # Test analysis  
        results = analyzer.analyze(  
            text="My Aadhaar is 234123412346",  
            language="en"  
        )  
          
        # Should detect Aadhaar  
        assert any(r.entity_type == "IN_AADHAAR" for r in results)  
  
    def test_create_analyzer_multiple_countries(self):  
        """Test creating analyzer with multiple countries."""  
        analyzer = create_analyzer_with_countries(["IN", "US"])  
          
        # Test with mixed PII  
        results = analyzer.analyze(  
            text="SSN: 078-05-1120, Aadhaar: 234123412346",  
            language="en"  
        )  
          
        entity_types = {r.entity_type for r in results}  
        assert "US_SSN" in entity_types or "IN_AADHAAR" in entity_types  
  
    def test_create_analyzer_without_defaults(self):  
        """Test creating analyzer without default recognizers."""  
        analyzer = create_analyzer_with_countries(  
            ["IN"],  
            include_default_recognizers=False  
        )  
          
        assert isinstance(analyzer, AnalyzerEngine)  
  
  
class TestAddCountryRecognizersToAnalyzer:  
    """Test suite for add_country_recognizers_to_analyzer function."""  
  
    def test_add_recognizers_to_existing_analyzer(self):  
        """Test adding country recognizers to existing analyzer."""  
        analyzer = AnalyzerEngine()  
          
        # Add Indian recognizers  
        add_country_recognizers_to_analyzer(analyzer, ["IN"])  
          
        # Verify recognizers were added  
        recognizers = analyzer.registry.get_recognizers(  
            language="en",  
            all_fields=True  
        )  
          
        recognizer_names = {r.name for r in recognizers}  
        assert any("Aadhaar" in name for name in recognizer_names)  
  
    def test_add_multiple_countries(self):  
        """Test adding multiple countries to analyzer."""  
        analyzer = AnalyzerEngine()  
          
        add_country_recognizers_to_analyzer(analyzer, ["IN", "US", "UK"])  
          
        # Test analysis with mixed PII  
        results = analyzer.analyze(  
            text="SSN: 078-05-1120, NHS: 401 023 2137",  
            language="en"  
        )  
          
        # Should detect at least one entity  
        assert len(results) > 0  
  
  
# Fixtures  
@pytest.fixture  
def sample_indian_text():  
    """Sample text with Indian PII."""  
    return "My Aadhaar number is 234123412346 and PAN is ABCDE1234F"  
  
  
@pytest.fixture  
def sample_us_text():  
    """Sample text with US PII."""  
    return "My SSN is 078-05-1120 and passport is 123456789"