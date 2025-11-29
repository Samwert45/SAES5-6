from rules_engine import RulesEngine

def test_basic_rules():
    engine = RulesEngine()
    
    # Test données
    attributes = {
        "firstname": "Jean",
        "lastname": "Dupont",
        "department": "IT"
    }
    
    # Appliquer les règles
    result = engine.apply_rules("ldap", attributes)
    
    # Vérifications
    assert result['login'] == "jean.dupont"
    assert result['cn'] == "Jean Dupont"
    assert result['mail'] == "jean.dupont@entreprise.com"
    assert result['dn'] == "uid=jean.dupont,dc=entreprise,dc=com"
    
    print("✅ Tests réussis!")
    print(f"Résultat: {result}")

if __name__ == "__main__":
    test_basic_rules()
