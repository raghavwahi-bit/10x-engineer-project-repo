import { useState } from 'react';
import { Outlet, useSearchParams } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import useCollections from '../hooks/useCollections';
import useTheme from '../hooks/useTheme';

export default function Layout() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { collections, create: createCollection, remove: removeCollection } = useCollections();
  const { dark, toggle: toggleTheme } = useTheme();

  const search = searchParams.get('search') || '';
  const collectionId = searchParams.get('collection') || null;

  const handleSearchChange = (value) => {
    const params = new URLSearchParams(searchParams);
    if (value) params.set('search', value);
    else params.delete('search');
    setSearchParams(params);
  };

  const handleSelectCollection = (id) => {
    const params = new URLSearchParams(searchParams);
    if (id) params.set('collection', id);
    else params.delete('collection');
    setSearchParams(params);
    setSidebarOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header
        search={search}
        onSearchChange={handleSearchChange}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        dark={dark}
        onToggleTheme={toggleTheme}
      />
      <div className="flex">
        <Sidebar
          collections={collections}
          activeCollectionId={collectionId}
          onSelectCollection={handleSelectCollection}
          onCreateCollection={createCollection}
          onDeleteCollection={removeCollection}
          isOpen={sidebarOpen}
        />
        {sidebarOpen && (
          <div className="fixed inset-0 bg-black/30 z-30 lg:hidden" onClick={() => setSidebarOpen(false)} />
        )}
        <main className="flex-1 p-6 min-h-[calc(100vh-57px)]">
          <Outlet context={{ search, collectionId, collections }} />
        </main>
      </div>
    </div>
  );
}
