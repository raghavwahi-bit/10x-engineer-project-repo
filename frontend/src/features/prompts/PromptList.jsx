import { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import PromptCard from './PromptCard';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';
import EmptyState from '../../components/EmptyState';
import ConfirmDialog from '../../components/ConfirmDialog';
import { getPromptTags } from '../../api/prompts';

export default function PromptList({ prompts: initialPrompts, loading, error, onRetry, onDelete, onCreateNew }) {
  const [deleteId, setDeleteId] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [promptTags, setPromptTags] = useState({});
  const [orderedPrompts, setOrderedPrompts] = useState([]);

  useEffect(() => {
    setOrderedPrompts(initialPrompts);
  }, [initialPrompts]);

  useEffect(() => {
    if (!orderedPrompts.length) return;
    const fetchTags = async () => {
      const tagsMap = {};
      await Promise.all(
        orderedPrompts.map(async (p) => {
          try {
            const data = await getPromptTags(p.id);
            tagsMap[p.id] = data.tags;
          } catch {
            tagsMap[p.id] = [];
          }
        })
      );
      setPromptTags(tagsMap);
    };
    fetchTags();
  }, [orderedPrompts]);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await onDelete(deleteId);
      setDeleteId(null);
    } catch {
      // error handled by parent
    } finally {
      setDeleting(false);
    }
  };

  const handleDragEnd = (result) => {
    if (!result.destination) return;
    const items = Array.from(orderedPrompts);
    const [reordered] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reordered);
    setOrderedPrompts(items);
  };

  if (loading) return <LoadingSpinner message="Loading prompts..." />;
  if (error) return <ErrorMessage message={error} onRetry={onRetry} />;
  if (!orderedPrompts.length) {
    return (
      <EmptyState
        title="No prompts yet"
        description="Create your first prompt to get started."
        actionLabel="New Prompt"
        onAction={onCreateNew}
      />
    );
  }

  return (
    <>
      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="prompts" direction="horizontal">
          {(provided) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              {orderedPrompts.map((prompt, index) => (
                <Draggable key={prompt.id} draggableId={prompt.id} index={index}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      className={snapshot.isDragging ? 'opacity-80 rotate-1' : ''}
                    >
                      <PromptCard
                        prompt={prompt}
                        tags={promptTags[prompt.id] || []}
                        onDelete={setDeleteId}
                        dragHandleProps={provided.dragHandleProps}
                      />
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>

      <ConfirmDialog
        isOpen={!!deleteId}
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
        title="Delete Prompt"
        message="Are you sure you want to delete this prompt? This action cannot be undone."
        loading={deleting}
      />
    </>
  );
}
