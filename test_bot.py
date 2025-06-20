import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.telegram_bot import TelegramDomainBot
from src.models.domain import db, Domain
from flask import Flask
import asyncio

class TestTelegramBot(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        
        db.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()
        
        # Create bot instance (without real token for testing)
        self.bot = TelegramDomainBot("test_token", self.app.app_context)
    
    def test_domain_validation(self):
        """Test domain validation function"""
        # Valid domains
        self.assertTrue(self.bot.is_valid_domain("google.com"))
        self.assertTrue(self.bot.is_valid_domain("sub.domain.com"))
        self.assertTrue(self.bot.is_valid_domain("example.org"))
        
        # Invalid domains
        self.assertFalse(self.bot.is_valid_domain(""))
        self.assertFalse(self.bot.is_valid_domain("invalid"))
        self.assertFalse(self.bot.is_valid_domain("http://google.com"))
        self.assertFalse(self.bot.is_valid_domain("google..com"))
    
    def test_check_domain_status(self):
        """Test domain status checking"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Test with known unblocked domain
            result = loop.run_until_complete(self.bot.check_domain_status("google.com"))
            self.assertIsInstance(result, dict)
            self.assertIn('blocked', result)
            self.assertFalse(result['blocked'])
            
            # Test with known blocked domain
            result = loop.run_until_complete(self.bot.check_domain_status("reddit.com"))
            self.assertIsInstance(result, dict)
            self.assertIn('blocked', result)
            self.assertTrue(result['blocked'])
            
        finally:
            loop.close()
    
    def test_database_operations(self):
        """Test database operations"""
        with self.app.app_context():
            # Test adding domain
            domain = Domain(
                user_id=12345,
                domain="test.com",
                status=False
            )
            db.session.add(domain)
            db.session.commit()
            
            # Test retrieving domain
            retrieved = Domain.query.filter_by(user_id=12345, domain="test.com").first()
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.domain, "test.com")
            self.assertFalse(retrieved.status)
            
            # Test updating domain
            retrieved.status = True
            db.session.commit()
            
            updated = Domain.query.filter_by(user_id=12345, domain="test.com").first()
            self.assertTrue(updated.status)
            
            # Test deleting domain
            db.session.delete(updated)
            db.session.commit()
            
            deleted = Domain.query.filter_by(user_id=12345, domain="test.com").first()
            self.assertIsNone(deleted)

if __name__ == '__main__':
    print("🧪 Running tests for Telegram Domain Checker Bot...")
    unittest.main(verbosity=2)

