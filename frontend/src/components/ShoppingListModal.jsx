import React, { useState } from 'react';
import './ShoppingListModal.css';

const ShoppingListModal = ({ shoppingList, isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('list');
  const [checkedItems, setCheckedItems] = useState({});

  if (!isOpen || !shoppingList) return null;

  const toggleItem = (itemId) => {
    setCheckedItems((prev) => ({
      ...prev,
      [itemId]: !prev[itemId],
    }));
  };

  const copyToClipboard = () => {
    const text = shoppingList
      .map(
        (category) =>
          `${category.category}\n${category.items
            .map((item) => `  ☐ ${item.name} - ${item.quantity} ${item.unit}`)
            .join('\n')}`
      )
      .join('\n\n');
    navigator.clipboard.writeText(text);
    alert('Shopping list copied to clipboard!');
  };

  const printList = () => {
    window.print();
  };

  const downloadPDF = () => {
    // Placeholder for PDF download
    alert('PDF download coming soon!');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="shopping-list-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">🛒 Shopping List</h2>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-actions">
          <button className="action-btn copy-btn" onClick={copyToClipboard}>
            📋 Copy
          </button>
          <button className="action-btn print-btn" onClick={printList}>
            🖨️ Print
          </button>
          <button className="action-btn download-btn" onClick={downloadPDF}>
            💾 Download
          </button>
        </div>

        <div className="modal-tabs">
          <button
            className={`tab-btn ${activeTab === 'list' ? 'active' : ''}`}
            onClick={() => setActiveTab('list')}
          >
            📝 List View
          </button>
          <button
            className={`tab-btn ${activeTab === 'checklist' ? 'active' : ''}`}
            onClick={() => setActiveTab('checklist')}
          >
            ✓ Checklist
          </button>
          <button
            className={`tab-btn ${activeTab === 'print' ? 'active' : ''}`}
            onClick={() => setActiveTab('print')}
          >
            🔍 Preview
          </button>
        </div>

        <div className="modal-content">
          {activeTab === 'list' && (
            <div className="list-view">
              {shoppingList.map((category, idx) => (
                <div key={idx} className="category-section">
                  <h3 className="category-title">{category.category}</h3>
                  <ul className="items-list">
                    {category.items.map((item, itemIdx) => (
                      <li key={itemIdx} className="list-item">
                        <span className="item-checkbox">☐</span>
                        <span className="item-name">{item.name}</span>
                        <span className="item-quantity">
                          {item.quantity} {item.unit}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'checklist' && (
            <div className="checklist-view">
              {shoppingList.map((category, idx) => (
                <div key={idx} className="category-section">
                  <h3 className="category-title">{category.category}</h3>
                  <div className="items-checklist">
                    {category.items.map((item, itemIdx) => {
                      const itemId = `${idx}-${itemIdx}`;
                      const isChecked = checkedItems[itemId];
                      return (
                        <label key={itemId} className="checklist-item">
                          <input
                            type="checkbox"
                            checked={isChecked || false}
                            onChange={() => toggleItem(itemId)}
                          />
                          <span className={`checkbox-visual ${isChecked ? 'checked' : ''}`}>
                            {isChecked ? '✓' : ''}
                          </span>
                          <span className={`item-label ${isChecked ? 'checked' : ''}`}>
                            {item.name}
                          </span>
                          <span className="item-qty-label">
                            {item.quantity} {item.unit}
                          </span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              ))}
              <div className="checklist-progress">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${
                        Object.values(checkedItems).filter(Boolean).length === 0
                          ? 0
                          : (Object.values(checkedItems).filter(Boolean).length /
                              shoppingList.reduce(
                                (acc, cat) => acc + cat.items.length,
                                0
                              )) *
                            100
                      }%`,
                    }}
                  />
                </div>
                <p className="progress-text">
                  {Object.values(checkedItems).filter(Boolean).length} /{' '}
                  {shoppingList.reduce((acc, cat) => acc + cat.items.length, 0)} items
                </p>
              </div>
            </div>
          )}

          {activeTab === 'print' && (
            <div className="print-view">
              <div className="print-header">
                <h2>EatRight Shopping List</h2>
                <p>Generated on {new Date().toLocaleDateString()}</p>
              </div>
              {shoppingList.map((category, idx) => (
                <div key={idx} className="print-category">
                  <h3>{category.category}</h3>
                  <table className="print-table">
                    <tbody>
                      {category.items.map((item, itemIdx) => (
                        <tr key={itemIdx}>
                          <td className="print-checkbox">☐</td>
                          <td className="print-name">{item.name}</td>
                          <td className="print-quantity">
                            {item.quantity} {item.unit}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ShoppingListModal;
