import { useState } from 'react';
import CollectionList from '../features/collections/CollectionList';
import CollectionForm from '../features/collections/CollectionForm';
import Modal from '../components/Modal';
import Button from '../components/Button';
import ConfirmDialog from '../components/ConfirmDialog';

export default function Sidebar({ collections, activeCollectionId, onSelectCollection, onCreateCollection, onDeleteCollection, isOpen }) {
  const [showForm, setShowForm] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [deleteError, setDeleteError] = useState(null);

  const handleCreate = async (data) => {
    await onCreateCollection(data);
    setShowForm(false);
  };

  const handleDelete = async () => {
    setDeleteError(null);
    try {
      await onDeleteCollection(deleteId);
      setDeleteId(null);
    } catch (err) {
      setDeleteError(err.message);
    }
  };

  return (
    <>
      <aside className={`${isOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-transform duration-200 ease-in-out overflow-y-auto pt-16 lg:pt-0`}>
        <div className="p-4">
          <button
            onClick={() => onSelectCollection(null)}
            className={`w-full text-left px-3 py-2 text-sm rounded-md mb-2 transition-colors ${
              !activeCollectionId
                ? 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 font-medium'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            All Prompts
          </button>

          <div className="flex items-center justify-between mb-2 mt-4">
            <h2 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Collections</h2>
          </div>

          {collections.length === 0 ? (
            <p className="text-sm text-gray-400 px-3 py-2">No collections yet</p>
          ) : (
            <CollectionList
              collections={collections}
              activeId={activeCollectionId}
              onSelect={onSelectCollection}
              onDelete={setDeleteId}
            />
          )}

          <Button variant="secondary" size="sm" className="w-full mt-3" onClick={() => setShowForm(true)}>
            + New Collection
          </Button>
        </div>
      </aside>

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="New Collection">
        <CollectionForm onSubmit={handleCreate} onCancel={() => setShowForm(false)} />
      </Modal>

      <ConfirmDialog
        isOpen={!!deleteId}
        onConfirm={handleDelete}
        onCancel={() => { setDeleteId(null); setDeleteError(null); }}
        title="Delete Collection"
        message={deleteError || 'Are you sure? Collections with prompts cannot be deleted.'}
        loading={false}
      />
    </>
  );
}
