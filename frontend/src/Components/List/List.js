import Element from '../Element/Element';
import './List.css';

function List({ elements, emptyHeading }) {
  const count = elements.length;
  let heading = emptyHeading;
  if (count > 0) {
    const noun = count > 1 ? 'Найдено' : 'Найдено';
    heading = count + ' ' + noun;
  }
  return (
    <section className='element-list'>
      <h2 className='primary'>{heading}</h2>

      <ul className='elements'>
        {elements.map(element => (
          <Element key={element.id} data={element} />
        ))}
      </ul>
    </section>
  );
}

export default List;
